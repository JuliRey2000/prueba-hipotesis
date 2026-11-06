"""Bloques para construir variables futuras."""
import numpy as np
import pandas as pd


def atr(df, n=14):
    """Rango verdadero medio de los últimos n días, hasta hoy."""
    C, H, L = df['Close'], df['High'], df['Low']
    rv = pd.concat([H - L, (H - C.shift(1)).abs(), (L - C.shift(1)).abs()], axis=1).max(axis=1)
    return rv.rolling(n).mean()


def resultado_regla_estudio(df, k_stop=1.0, n_atr=14):
    """R de comprar al cierre de hoy, stop a k·ATR por debajo, salida al cierre de mañana.

    Si mañana el mínimo toca el stop, sale en el stop; si abre por debajo (gap), sale en la apertura.
    """
    C, L, O = df['Close'], df['Low'], df['Open']
    riesgo = k_stop * atr(df, n_atr)
    stop = C - riesgo
    res = (C.shift(-1) - C) / riesgo
    toca = L.shift(-1) <= stop
    return res.where(~toca, (np.minimum(O.shift(-1), stop) - C) / riesgo).round(10)
