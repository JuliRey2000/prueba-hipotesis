"""Dónde se guardan las pruebas: Google Drive, fichas e índice general de hipótesis."""
import os
from datetime import datetime

import pandas as pd

CARPETA_DRIVE = '/content/drive/MyDrive/Mentoria_Quant/hipotesis'
INDICE = 'indice_hipotesis.csv'


def conectar_drive(carpeta=CARPETA_DRIVE):
    """Monta Google Drive (solo en Colab), crea la carpeta y la devuelve.

    Fuera de Colab no falla: avisa y guarda en la carpeta local ./hipotesis.
    """
    try:
        from google.colab import drive
    except ImportError:
        carpeta = os.path.abspath('hipotesis')
        print('⚠ No estás en Colab: se guarda en la carpeta local', carpeta)
    else:
        drive.mount('/content/drive')
    os.makedirs(carpeta, exist_ok=True)
    print('Guardando en:', carpeta)
    return carpeta


def fila_indice(h, r):
    """Resumen de una hipótesis en una fila."""
    from .estadistica import medir
    m, p = r['medicion_prueba'], r['p_prueba']
    return {'id': h['id'], 'registrada': r['registro']['fecha'], 'huella': r['registro']['huella'][:16],
            'condicion': h['condicion'], 'variante_elegida': str(r['elegida']),
            'dif_construccion': round(float(medir(r['construccion'], h['costo_R'])['diferencia']), 4),
            'prueba_abierta': m is not None,
            'dif_prueba': None if m is None else round(float(m['diferencia']), 4),
            'p_prueba': None if p is None else round(float(p), 4),
            'mde': round(float(r['mde']), 3), 'veredicto': r['veredicto'],
            'actualizada': datetime.now().isoformat(timespec='seconds')}


def guardar_en_indice(fila, carpeta='.'):
    """Agrega la fila al índice; si el id ya estaba, reemplaza su fila. Devuelve el índice completo."""
    ruta = os.path.join(carpeta, INDICE)
    idx = pd.read_csv(ruta) if os.path.exists(ruta) else pd.DataFrame()
    if len(idx):
        idx = idx[idx['id'] != fila['id']]
    idx = pd.concat([idx, pd.DataFrame([fila])], ignore_index=True)
    idx.to_csv(ruta, index=False)
    return idx


def guardar_ficha(h, texto, carpeta='.'):
    with open(os.path.join(carpeta, f"ficha_{h['id']}.txt"), 'w', encoding='utf-8') as f:
        f.write(texto)


def ver_indice(carpeta='.'):
    """Todas las hipótesis probadas en la carpeta."""
    ruta = os.path.join(carpeta, INDICE)
    if not os.path.exists(ruta):
        print('Todavía no hay hipótesis en el índice.')
        return pd.DataFrame()
    return pd.read_csv(ruta)
