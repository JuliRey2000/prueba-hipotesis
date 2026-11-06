"""Ejemplo: cuando el índice cierra en la parte baja de su rango (IBS bajo), ¿comprar al cierre rinde más mañana?"""
import prueba_hipotesis as ph

datos = ph.cargar_datos('arch')

HIPOTESIS = {
    'id': 'ibs_bajo',
    'datos': 'NASDAQ Composite, velas diarias (librería arch)',
    'condicion': 'Hoy el índice cerró en la parte baja de su rango: IBS = (C − L) / (H − L) < ibs_max',
    'variable_futura': 'R de comprar al cierre de hoy, stop a 1,5·ATR(14), salida al cierre de mañana',
    'comparacion': 'La misma operación en los días con IBS normal o alto',
    'afirmacion': 'E[R | condición] − E[R | sin condición] >= umbral y esperanza neta > 0',
    'hipotesis_nula': 'H0: E[R | condición] − E[R | sin condición] <= 0',
    'umbral_R': 0.05,
    'costo_R': 0.02,
    'alfa': 0.05,
    'variantes': [{'ibs_max': 0.10, 'k_stop': 1.5}, {'ibs_max': 0.20, 'k_stop': 1.5}],
    'regla_de_eleccion': 'la de mayor diferencia en construcción',
    'construccion': ['1999-01-01', '2010-12-31'],
    'prueba': ['2011-01-01', '2018-12-31'],
}


def condicion(df, **p):
    rango = df['High'] - df['Low']
    ibs = (df['Close'] - df['Low']) / rango.where(rango > 0)
    return ibs < p['ibs_max']


def resultado_R(df, **p):
    return ph.resultado_regla_estudio(df, k_stop=p['k_stop'])


if __name__ == '__main__':
    carpeta = ph.conectar_drive()          # en Colab: Drive; fuera de Colab: ./hipotesis
    resultado = ph.validar(HIPOTESIS, datos, condicion, resultado_R, carpeta=carpeta)
