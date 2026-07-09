import pandas as pd
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    """
    Tính toán các features dựa trên cột Date hoặc index

    Args:
        df: DataFrame

    Returns:
        DataFrame gốc được bổ sung cột features mới.
    """
    df['hour'] = df.index.hour
    df['minute'] = df.index.minute
    df['day_of_month'] = df.index.day
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['day_of_week'] = df.index.dayofweek
    df['time_int'] = df['hour'] * 100 + df['minute']
    df["trade_date"] = df.index.normalize()
    df["bar_in_day"] = df.groupby("trade_date").cumcount()
    df["session_0930_1335"] = (df["time_int"] >= 930) & (df["time_int"] <= 1335)
    df["session_0935_1425"] = (df["time_int"] >= 935) & (df["time_int"] < 1425)
    df["session_0935_1335"] = (df["time_int"] >= 935) & (df["time_int"] <= 1335)
    df["late_session_1325"] = df["time_int"].isin({1325, 1340, 1355})
    df["late_session_1310"] = df["time_int"].isin({1310, 1325, 1340, 1355})
    df["entry_window_1300_1425"] = (df["time_int"] >= 1300) & (df["time_int"] <= 1425)
    df["session_progress"] = ((df.hour * 60 + df.minute) - 9 * 60) / (51 * 5)

    return df
