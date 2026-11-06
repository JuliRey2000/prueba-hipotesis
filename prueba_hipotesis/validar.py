"""Flujo completo: pre-registro → construcción → MDE → candado y veredicto → ficha."""
import os

import pandas as pd
from statsmodels.stats.multitest import multipletests

from .estadistica import armar_tabla, medir, prueba_permutacion, efecto_minimo_detectable, veredicto, ver
from .graficos import grafico_azar, estilo
from .registro import huella, preregistrar, mira_el_futuro, abrir_candado
from .almacen import fila_indice, guardar_en_indice, guardar_ficha

CAMPOS = ['id', 'condicion', 'variable_futura', 'umbral_R', 'costo_R', 'alfa',
          'variantes', 'regla_de_eleccion', 'construccion', 'prueba']


def _revisar(h):
    faltan = [c for c in CAMPOS if c not in h]
    if faltan:
        raise ValueError(f'Faltan campos en la hipótesis: {faltan}')
    if pd.Timestamp(h['prueba'][0]) <= pd.Timestamp(h['construccion'][1]):
        raise ValueError('Las fechas de prueba deben ser posteriores a las de construcción')
    if not h['variantes']:
        raise ValueError('Escribe al menos una variante (puede ser [{}])')


def construir(h, datos, condicion, resultado_R, n_perm=5000, graficar=True, carpeta='.'):
    """Paso 5: mide cada variante solo en construcción, corrige con Holm y elige con la regla escrita.

    La regla de elección implementada es 'la de mayor diferencia en construcción'.
    """
    ini_c, fin_c = h['construccion']
    filas = []
    for v in h['variantes']:
        t = armar_tabla(datos, v, condicion, resultado_R).loc[ini_c:fin_c].iloc[:-1]   # embargo de 1 día
        m = medir(t, h['costo_R'])
        _, p, _ = prueba_permutacion(t, n=n_perm)
        filas.append({**v, 'casos': int(m['casos con condición']), 'diferencia': m['diferencia'],
                      'esperanza neta': m['esperanza neta'], 'p': p})
    bitacora = pd.DataFrame(filas)
    bitacora['p (Holm)'] = multipletests(bitacora['p'], method='holm')[1]
    bitacora.to_csv(os.path.join(carpeta, f"bitacora_{h['id']}.csv"), index=False)
    print(bitacora.round(4).to_string(index=False))

    i = int(bitacora['diferencia'].idxmax())
    elegida = h['variantes'][i]
    construccion = armar_tabla(datos, elegida, condicion, resultado_R).loc[ini_c:fin_c].iloc[:-1]
    print(f"\nVariante elegida: {elegida}")
    ver(medir(construccion, h['costo_R']))
    if graficar:
        grafico_azar(*prueba_permutacion(construccion, n=n_perm), 'Construcción: ¿lo podría producir la suerte?')

    fila = bitacora.loc[i]
    pasa = bool(fila['diferencia'] >= h['umbral_R'] and fila['p (Holm)'] < h['alfa']
                and fila['esperanza neta'] > 0)
    print('✓ Pasa en construcción: tiene sentido abrir la prueba.' if pasa else
          '✗ No pasa ni en construcción: se recomienda archivarla y NO abrir la prueba.')
    return bitacora, elegida, construccion, pasa


def validar(h, datos, condicion, resultado_R, abrir_de_todos_modos=False,
            n_perm=5000, graficar=True, carpeta='.', indice=True):
    """Corre los pasos 4 a 8 del framework y devuelve un diccionario con todo el resultado.

    Guarda en `carpeta` el preregistro, la bitácora, la apertura, la ficha y (si indice=True)
    una fila en indice_hipotesis.csv. Usa carpeta=ph.conectar_drive() para dejarlo todo en Drive.

    h            diccionario HIPOTESIS
    datos        DataFrame con Open, High, Low, Close
    condicion    función (df, **params) -> Serie booleana, solo con información hasta ese día
    resultado_R  función (df, **params) -> Serie con el R de la operación abierta ese día
    """
    estilo()
    _revisar(h)
    os.makedirs(carpeta, exist_ok=True)

    print('── 4 · Pre-registro y regla de oro ──')
    registro = preregistrar(h, carpeta)
    for v in h['variantes']:
        falla = mira_el_futuro(condicion, datos, **v)
        print(f"Condición con {v}: {'✗ MIRA EL FUTURO' if falla else '✓ solo usa información disponible'}")
        if falla:
            raise ValueError('La condición usa información del futuro: corrígela antes de seguir')

    print('\n── 5 · Construcción ──')
    bitacora, elegida, construccion, pasa = construir(h, datos, condicion, resultado_R, n_perm, graficar, carpeta)

    print('\n── 6 · ¿Alcanzan los datos de prueba? ──')
    ini_p, fin_p = h['prueba']
    cond_prueba = condicion(datos, **elegida).loc[ini_p:fin_p].iloc[:-1].fillna(False).astype(bool)
    n_con, n_sin = int(cond_prueba.sum()), int((~cond_prueba).sum())
    mde = efecto_minimo_detectable(construccion, n_con, n_sin) if n_con > 0 and n_sin > 0 else float('inf')
    print(f"Casos con condición en prueba: {n_con}")
    print(f"Efecto mínimo detectable (80 %): {mde:.3f} R   ·   umbral escrito: {h['umbral_R']:.3f} R")
    if mde > h['umbral_R']:
        print("La prueba no puede detectar un efecto del tamaño del umbral: un resultado tibio saldrá 'no concluyente'.")

    print('\n── 7 · Candado y veredicto ──')
    m_prueba = p_prueba = None
    if pasa or abrir_de_todos_modos:
        print('Hipótesis evaluada = registrada:', '✓' if huella(h) == registro['huella'] else '✗ CAMBIÓ')
        abrir_candado(h, carpeta)
        prueba = armar_tabla(datos, elegida, condicion, resultado_R).loc[ini_p:fin_p]
        m_prueba = medir(prueba, h['costo_R'])
        real, p_prueba, azar = prueba_permutacion(prueba, n=n_perm)
        ver(pd.DataFrame({'construcción': medir(construccion, h['costo_R']), 'prueba': m_prueba}))
        if graficar:
            grafico_azar(real, p_prueba, azar, 'Prueba: el examen de verdad')
        print(f"\nDiferencia en prueba: {m_prueba['diferencia']:+.4f} R   ·   p = {p_prueba:.4f}")
        resultado = veredicto(m_prueba, p_prueba, h)
    else:
        resultado = 'RECHAZADA EN CONSTRUCCIÓN (la prueba sigue sin abrir)'
    print('VEREDICTO:', resultado)

    out = {'registro': registro, 'bitacora': bitacora, 'elegida': elegida, 'construccion': construccion,
           'pasa_construccion': pasa, 'mde': mde, 'medicion_prueba': m_prueba, 'p_prueba': p_prueba,
           'veredicto': resultado}
    print('\n── 8 · Ficha ──')
    texto = ficha(h, out)
    print(texto)
    guardar_ficha(h, texto, carpeta)
    if indice:
        idx = guardar_en_indice(fila_indice(h, out), carpeta)
        print(f"\n✓ Guardada en el índice ({len(idx)} hipótesis en total) · {os.path.abspath(carpeta)}")
    return out


def ficha(h, r):
    """La hipótesis en una página, lista para copiar a la bitácora."""
    m, p = r['medicion_prueba'], r['p_prueba']
    texto_prueba = ('sin abrir' if m is None else
                    f"diferencia {m['diferencia']:+.3f} R, p = {p:.4f}, esperanza neta {m['esperanza neta']:+.3f} R")
    dif_c = medir(r['construccion'], h['costo_R'])['diferencia']
    reg = r['registro']
    return f"""HIPÓTESIS: {h['id']}                Registrada: {reg['fecha']}   Huella: {reg['huella'][:16]}…

1. DATOS              {h.get('datos', '')}
2. CONDICIÓN          {h['condicion']}
3. VARIABLE FUTURA    {h['variable_futura']}
4. COMPARACIÓN        {h.get('comparacion', '')}
5. AFIRMACIÓN         {h.get('afirmacion', '')}   (umbral {h['umbral_R']} R, costo {h['costo_R']} R)
6. HIPÓTESIS NULA     {h.get('hipotesis_nula', '')}
7. ELECCIÓN           {len(h['variantes'])} variantes, {h['regla_de_eleccion']} → {r['elegida']}
8. PLAN               construcción {h['construccion'][0]} a {h['construccion'][1]}   ·   prueba {h['prueba'][0]} a {h['prueba'][1]} (una vez)
                      efecto mínimo detectable en prueba: {r['mde']:.3f} R
9. RESULTADO          construcción: diferencia {dif_c:+.3f} R
                      prueba:       {texto_prueba}
   VEREDICTO          {r['veredicto']}"""
