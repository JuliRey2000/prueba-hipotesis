# prueba-hipotesis

Motor para validar hipótesis de trading sin engañarte a ti mismo · Mentoría Quant · Castle Capital.

Hace en una sola llamada todo el framework: **pre-registro con huella**, **regla de no mirar el futuro**, **construcción con prueba de permutación y corrección de Holm**, **efecto mínimo detectable**, **candado de la prueba fuera de muestra** y **ficha final**.

## Instalación

En Colab o en tu computador:

```python
%pip install -q git+https://github.com/JuliRey2000/prueba-hipotesis.git
```

Si el repositorio es privado, usa un token personal de GitHub:

```python
%pip install -q git+https://TU_TOKEN@github.com/JuliRey2000/prueba-hipotesis.git
```

Para usar Yahoo Finance: `pip install "prueba-hipotesis[yahoo] @ git+https://github.com/JuliRey2000/prueba-hipotesis.git"`

## Uso: solo escribes 3 cosas

```python
import numpy as np
import prueba_hipotesis as ph

datos = ph.cargar_datos('arch')            # o ph.cargar_datos('yahoo', 'QQQ', '2005-01-01')

HIPOTESIS = {
    'id': 'caida_fuerte',
    'condicion': 'Hoy el índice cayó más de 2 %',
    'variable_futura': 'R de comprar al cierre, stop a k·ATR(14), salida al cierre de mañana',
    'umbral_R': 0.05, 'costo_R': 0.02, 'alfa': 0.05,
    'variantes': [{'k_stop': 1.0}, {'k_stop': 2.0}],
    'regla_de_eleccion': 'la de mayor diferencia en construcción',
    'construccion': ['1999-01-01', '2010-12-31'],
    'prueba': ['2011-01-01', '2018-12-31'],
}

def condicion(df, **p):                     # solo información hasta ese día
    return np.log(df['Close'] / df['Close'].shift(1)) < -0.02

def resultado_R(df, **p):                   # resultado en R de la operación abierta ese día
    return ph.resultado_regla_estudio(df, k_stop=p['k_stop'])

r = ph.validar(HIPOTESIS, datos, condicion, resultado_R)
print(r['veredicto'])
```

Campos opcionales de la hipótesis (aparecen en la ficha): `datos`, `comparacion`, `afirmacion`, `hipotesis_nula`.

`validar` acepta además:

| Parámetro | Por defecto | Qué hace |
|---|---|---|
| `abrir_de_todos_modos` | `False` | Abre la prueba aunque no pase en construcción (solo para practicar) |
| `carpeta` | `'.'` | Dónde se guardan preregistro, bitácora y apertura |
| `n_perm` | `5000` | Permutaciones de la prueba del azar |
| `graficar` | `True` | Muestra los histogramas del azar |
| `indice` | `True` | Guarda la ficha y agrega la hipótesis a `indice_hipotesis.csv` |

Devuelve un diccionario con `registro`, `bitacora`, `elegida`, `construccion`, `pasa_construccion`, `mde`, `medicion_prueba`, `p_prueba` y `veredicto`.

## Funciones sueltas

Si prefieres armar tu propio flujo paso a paso:

| Módulo | Funciones |
|---|---|
| `datos` | `cargar_datos` |
| `reglas` | `atr`, `resultado_regla_estudio` |
| `registro` | `huella`, `preregistrar`, `mira_el_futuro`, `abrir_candado` |
| `estadistica` | `armar_tabla`, `medir`, `prueba_permutacion`, `efecto_minimo_detectable`, `veredicto`, `ver` |
| `validar` | `construir`, `validar`, `ficha` |
| `almacen` | `conectar_drive`, `ver_indice`, `guardar_en_indice`, `fila_indice` |

## Guardar todo en Google Drive

```python
carpeta = ph.conectar_drive()      # monta Drive y usa Mi unidad/Mentoria_Quant/hipotesis
r = ph.validar(HIPOTESIS, datos, condicion, resultado_R, carpeta=carpeta)
ph.ver_indice(carpeta)             # tabla con todas las hipótesis probadas
```

`conectar_drive('otra/ruta')` acepta cualquier carpeta. Fuera de Colab no falla: guarda en `./hipotesis`.

**Carpeta compartida (mentoría):** el mentor comparte `Mentoria_Quant` como editor; cada alumno, en Drive, hace clic derecho → *Organizar → Agregar acceso directo → Mi unidad*. Así todos escriben en el mismo índice. Pon tu nombre en el `id` (`'julian_ibs_bajo'`) para no pisar archivos ajenos.

## Archivos que genera

- `preregistro_<id>.json`: la hipótesis, la fecha y su huella SHA-256. Si cambias la hipótesis, lo detecta.
- `bitacora_<id>.csv`: todas las variantes probadas en construcción, con p y p de Holm.
- `apertura_<id>.json`: cuándo se abrió la prueba. La segunda vez avisa que ya no es fuera de muestra.
- `ficha_<id>.txt`: la ficha final.
- `indice_hipotesis.csv`: una fila por hipótesis (veredicto, diferencias, p, MDE). Si repites un `id`, se actualiza su fila.

Sin Drive, en Colab esos archivos se borran al cerrar la sesión.

## Ejemplo completo

- `ejemplos/plantilla_colab.ipynb`: la plantilla para cada idea nueva.
- `ejemplos/caida_fuerte.py`: caída > 2 % → rechazada en construcción.
- `ejemplos/ibs_bajo.py`: cierre en la parte baja del rango → casi pasa, pero rechazada en construcción.
