"""prueba_hipotesis · Motor de validación de hipótesis de trading (Mentoría Quant · Castle Capital)."""
from .datos import cargar_datos
from .reglas import atr, resultado_regla_estudio
from .registro import huella, preregistrar, mira_el_futuro, abrir_candado
from .estadistica import armar_tabla, medir, prueba_permutacion, efecto_minimo_detectable, veredicto, ver
from .graficos import estilo, grafico_azar
from .validar import construir, validar, ficha

__version__ = '0.1.0'

__all__ = ['cargar_datos', 'atr', 'resultado_regla_estudio', 'huella', 'preregistrar', 'mira_el_futuro',
           'abrir_candado', 'armar_tabla', 'medir', 'prueba_permutacion', 'efecto_minimo_detectable',
           'veredicto', 'ver', 'estilo', 'grafico_azar', 'construir', 'validar', 'ficha']
