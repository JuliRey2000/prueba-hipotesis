"""Medición, prueba del azar, efecto mínimo detectable y veredicto."""
import numpy as np
import pandas as pd


def armar_tabla(df, params, condicion, resultado_R):
    """Una fila por día: si se cumplió la condición y el resultado en R."""
    t = pd.DataFrame({'cond': condicion(df, **params), 'R': resultado_R(df, **params)}).dropna()
    t['cond'] = t['cond'].astype(bool)
    return t


def medir(t, costo):
    """Esperanzas con y sin condición, diferencia, error estándar, IC 95 % y esperanza neta."""
    con, sin = t.loc[t['cond'], 'R'], t.loc[~t['cond'], 'R']
    if len(con) < 2 or len(sin) < 2:
        raise ValueError('La condición casi nunca (o casi siempre) se cumple: no hay con qué comparar')
    dif = con.mean() - sin.mean()
    ee = np.sqrt(con.var() / len(con) + sin.var() / len(sin))
    return pd.Series({'casos con condición': len(con), 'casos sin condición': len(sin),
                      'E[R | condición]': con.mean(), 'E[R | sin condición]': sin.mean(),
                      'diferencia': dif, 'error estándar': ee,
                      'IC 95 % inferior': dif - 1.96 * ee, 'IC 95 % superior': dif + 1.96 * ee,
                      'esperanza neta': con.mean() - costo})


def prueba_permutacion(t, n=5000, semilla=0):
    """p de una cola: proporción de permutaciones con diferencia ≥ la real."""
    rng = np.random.default_rng(semilla)
    r, marca = t['R'].to_numpy(), t['cond'].to_numpy().copy()
    real = r[marca].mean() - r[~marca].mean()
    azar = np.empty(n)
    for i in range(n):
        rng.shuffle(marca)
        azar[i] = r[marca].mean() - r[~marca].mean()
    return real, (1 + np.sum(azar >= real)) / (n + 1), azar


def efecto_minimo_detectable(t_construccion, n_con, n_sin, z=2.8):
    """MDE con potencia 80 % y alfa 5 % (1,96 + 0,84 ≈ 2,8), usando las desviaciones de construcción."""
    s_con = t_construccion.loc[t_construccion['cond'], 'R'].std()
    s_sin = t_construccion.loc[~t_construccion['cond'], 'R'].std()
    return z * np.sqrt(s_con ** 2 / n_con + s_sin ** 2 / n_sin)


def veredicto(m, p, h, imprimir=True):
    criterios = {f"diferencia ≥ {h['umbral_R']} R": m['diferencia'] >= h['umbral_R'],
                 f"p < {h['alfa']}": p < h['alfa'],
                 'esperanza neta > 0': m['esperanza neta'] > 0}
    if imprimir:
        for nombre, ok in criterios.items():
            print(f"  {'✓' if ok else '✗'} {nombre}")
    if m['diferencia'] <= 0 or m['esperanza neta'] <= 0:
        return 'RECHAZADA'
    return 'APOYADA (todavía no rechazada)' if all(criterios.values()) else 'NO CONCLUYENTE'


def ver(x):
    """Imprime una Serie o DataFrame con formato legible."""
    fmt = lambda v: f'{v:,.0f}' if float(v).is_integer() and abs(v) >= 1 else f'{v:+.4f}'
    print(x.map(fmt).to_string())
