"""Carga de datos diarios OHLC."""
import pandas as pd


def cargar_datos(fuente='arch', ticker='^IXIC', inicio='1999-01-01'):
    """NASDAQ Composite 1999–2018 (librería arch) o cualquier ticker diario de Yahoo Finance.

    fuente: 'arch' o 'yahoo'.
    """
    if fuente == 'arch':
        from arch.data import nasdaq
        return nasdaq.load()[['Open', 'High', 'Low', 'Close']]
    if fuente != 'yahoo':
        raise ValueError("fuente debe ser 'arch' o 'yahoo'")
    import yfinance as yf
    df = yf.download(ticker, start=inicio, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    if len(df) < 500:
        raise ValueError('Muy pocos datos: revisa el ticker o la conexión')
    return df
