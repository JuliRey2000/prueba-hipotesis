"""Pre-registro, regla de oro (no mirar el futuro) y candado de la prueba."""
import hashlib
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd


def huella(h):
    """SHA-256 de la hipótesis: cambia si cambia cualquier campo."""
    texto = json.dumps(h, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def preregistrar(h, carpeta='.'):
    """Guarda la hipótesis con fecha y huella. Si ya existe, avisa si cambió."""
    archivo = os.path.join(carpeta, f"preregistro_{h['id']}.json")
    if os.path.exists(archivo):
        with open(archivo, encoding='utf-8') as f:
            previo = json.load(f)
        estado = '✓ sin cambios' if previo['huella'] == huella(h) else '✗ LA HIPÓTESIS CAMBIÓ desde el registro'
        print(f"Ya registrada el {previo['fecha']}: {estado}")
        return previo
    registro = {'fecha': datetime.now().isoformat(timespec='seconds'), 'huella': huella(h), 'hipotesis': h}
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(registro, f, ensure_ascii=False, indent=2, default=str)
    print(f"Registrada el {registro['fecha']}   ·   huella: {registro['huella']}")
    return registro


def mira_el_futuro(funcion, df, n_fechas=150, semilla=1, **params):
    """True si `funcion` cambia su valor en alguna fecha al cortar los datos en esa fecha."""
    completo = funcion(df, **params)
    fechas = np.random.default_rng(semilla).choice(df.index[60:-30], n_fechas, replace=False)
    for f in fechas:
        a, b = completo.loc[f], funcion(df.loc[:f], **params).loc[f]
        if not (a == b or (pd.isna(a) and pd.isna(b))):
            return True
    return False


def abrir_candado(h, carpeta='.'):
    """Deja constancia de cuándo se abrió la prueba; avisa si ya se había abierto."""
    archivo = os.path.join(carpeta, f"apertura_{h['id']}.json")
    if os.path.exists(archivo):
        with open(archivo, encoding='utf-8') as f:
            fecha = json.load(f)['fecha']
        print(f"⚠ La prueba ya se abrió el {fecha}. "
              "Si ajustaste algo después de mirarla, ya no es fuera de muestra.")
        return False
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump({'fecha': datetime.now().isoformat(timespec='seconds'), 'huella': huella(h)}, f)
    return True
