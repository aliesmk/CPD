import talib


def detect_trend(df, period=50, method='sma'):
    """
    تشخیص روند با SMA یا EMA
    """
    if method == 'sma':
        df['ma'] = talib.SMA(df['close'], timeperiod=period)
    elif method == 'ema':
        df['ma'] = talib.EMA(df['close'], timeperiod=period)

    df['trend'] = 'neutral'
    df.loc[df['close'] > df['ma'], 'trend'] = 'up'
    df.loc[df['close'] < df['ma'], 'trend'] = 'down'
    return df