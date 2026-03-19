import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df['cs_body'] = df.apply(lambda r: r["Close"] - r["Open"], axis=1)
    df['cs_height'] = df.apply(lambda r: r["High"] - r["Low"], axis=1)
    df['cs_upwick'] = df.apply(lambda r: r["High"] - max(r["Open"], r["Close"]), axis=1)
    df['cs_lowwick'] = df.apply(lambda r: min(r["Open"], r["Close"]) - r["Low"], axis=1)
    df['cs_upwick_rate'] = df.apply(lambda r: 1 if r["cs_height"] == 0 else round(r["cs_upwick"] * 100 / r["cs_height"], 3), axis=1)
    df['cs_lowwick_rate'] = df.apply(lambda r: 1 if r["cs_height"] == 0 else round(r["cs_lowwick"] * 100 / r["cs_height"], 3), axis=1)
    df['cs_ibs'] = df.apply(lambda r: 1 if r["cs_height"] == 0 else (r["Close"] - r["Low"]) / r["cs_height"], axis=1)
    df['cs_color'] = df.apply(lambda r: 'doji' if r["cs_body"] == 0 else ('green' if r["cs_body"] > 0 else 'red'), axis=1)
    return df