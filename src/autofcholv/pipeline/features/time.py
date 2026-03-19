import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
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
    df["session_progress"] = ((df.hour * 60 + df.minute) - 9 * 60) / (51 * 5) # update by config in .env later

    return df