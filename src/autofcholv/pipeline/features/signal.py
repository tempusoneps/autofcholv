import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df['couple_cs_signal'] = df.apply(get_couple_candleticks_signal, axis=1)
    df["ema20_250_cross_signal"] = df.apply(get_ema20_250_cross_signal, axis=1)
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
    signal = ''
    if _1st_cond == 'S' and _2nd_cond == 'S':
        signal = 'short'
    elif _1st_cond == 'L' and _2nd_cond == 'L':
        signal = 'long'
    return signal


def get_ema20_250_cross_signal(r):
    signal = ''
    if r['ema20'] > r['ema250'] and r['prev_ema20'] <= r['prev_ema250']:
        signal = 'long'
    elif r['ema20'] < r['ema250'] and r['prev_ema20'] >= r['prev_ema250']:
        signal = 'short'
    return signal