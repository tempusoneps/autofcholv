import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df['couple_cs_signal'] = df.apply(get_couple_candleticks_signal, axis=1)
    df["ema_cross_signal"] = df.apply(get_ema_cross_signal, axis=1)
    return df
    

def get_couple_candleticks_signal(r):
    _1st_cond = ''
    if r['Open'] > r['Close'] >= r['Low'] + 0.1:
        # Do va co bong nen duoi
        _1st_cond = 'S'
    elif r['Open'] < r['Close'] <= r['High'] - 0.1:
        # Xanh va co bong nen tren
        _1st_cond = 'L'
    _2nd_cond = ''
    if r['Open'] > r['Close'] == r['Low'] and r['Low'] < r['prev_Low']:
        # Do va khong co bong nen duoi
        _2nd_cond = 'S'
    elif r['Open'] < r['Close'] == r['High'] and r['High'] > r['prev_High']:
        # Xanh va khong co bong nen tren
        _2nd_cond = 'L'
    signal = 'None'
    if _1st_cond == 'S' and _2nd_cond == 'S':
        signal = 'Bearish'
    elif _1st_cond == 'L' and _2nd_cond == 'L':
        signal = 'Bullish'
    return signal


def get_ema_cross_signal(r):
    signal = 'None'
    if r['ema_fast'] > r['ema_slow'] and r['prev_ema_fast'] <= r['prev_ema_slow']:
        signal = 'Bullish'
    elif r['ema_fast'] < r['ema_slow'] and r['prev_ema_fast'] >= r['prev_ema_slow']:
        signal = 'Bearish'
    return signal