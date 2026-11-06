"""Ejemplo: después de una caída fuerte, ¿comprar al cierre rinde más que en un día normal?"""
import numpy as np
import prueba_hipotesis as ph

datos = ph.cargar_datos('arch')

HIPOTESIS = {
    'id': 'caida_fuerte',
    'datos': 'NASDAQ Composite, velas diarias (librería arch)',
    'condicion': 'Hoy el índice cayó más de 2 % (se conoce al cierre de hoy)',
    'variable_futura': 'R de comprar al cierre de hoy, stop a k·ATR(14), salida al cierre de mañana',
    'comparacion': 'La misma operación en los días sin caída fuerte',
    'afirmacion': 'E[R | condición] − E[R | sin condición] >= umbral y esperanza neta > 0',
    'hipotesis_nula': 'H0: E[R | condición] − E[R | sin condición] <= 0',
    'umbral_R': 0.05,
    'costo_R': 0.02,
    'alfa': 0.05,
    'variantes': [{'k_stop': 1.0}, {'k_stop': 2.0}],
    'regla_de_eleccion': 'la de mayor diferencia en construcción',
    'construccion': ['1999-01-01', '2010-12-31'],
    'prueba': ['2011-01-01', '2018-12-31'],
}


def condicion(df, **p):
    ret = np.log(df['Close'] / df['Close'].shift(1))
    return ret < -0.02


def resultado_R(df, **p):
    return ph.resultado_regla_estudio(df, k_stop=p['k_stop'])


if __name__ == '__main__':
    resultado = ph.validar(HIPOTESIS, datos, condicion, resultado_R, carpeta='resultados')
