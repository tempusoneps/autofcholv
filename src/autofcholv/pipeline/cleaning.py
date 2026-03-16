import pandas as pd


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def clean_ohlcv(
    data: pd.DataFrame,
    dropna: bool = False,
    remove_negative: bool = False,
    remove_duplicates: bool = False,
    sort_by_index: bool = True,
) -> pd.DataFrame:
    """
    Clean OHLCV DataFrame với Date là index.
    """

    df = data.copy()

    # ==============================
    # 1️⃣ Validate index
    # ==============================
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            raise ValueError("DataFrame index must be DatetimeIndex or convertible to datetime")

    # ==============================
    # 2️⃣ Validate required columns
    # ==============================
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # ==============================
    # 3️⃣ Convert numeric columns
    # ==============================
    df[REQUIRED_COLUMNS] = df[REQUIRED_COLUMNS].apply(
        pd.to_numeric, errors="coerce"
    )

    # ==============================
    # 4️⃣ Drop NaN
    # ==============================
    if dropna:
        df = df.dropna(subset=REQUIRED_COLUMNS)
    else:
        findnan = df[df[REQUIRED_COLUMNS].isnull().any(axis=1)]
        if len(findnan):
            raise ValueError(f"There are {len(findnan)} rows with NaN values")

    # ==============================
    # 5️⃣ Remove negative values
    # ==============================
    if remove_negative:
        df = df[
            (df[["Open", "High", "Low", "Close"]] >= 0).all(axis=1)
            & (df["Volume"] >= 0)
        ]
    else:
        findneg = df[(df[["Open", "High", "Low", "Close"]] < 0).any(axis=1) | (df["Volume"] < 0)]
        if len(findneg):
            raise ValueError(f"There are {len(findneg)} rows with negative values")

    # ==============================
    # 6️⃣ Fix logical OHLC errors
    # ==============================
    error_df = df[
        (df["High"] < df[["Open", "Close", "Low"]].max(axis=1))
        | (df["Low"] > df[["Open", "Close", "High"]].min(axis=1))
    ]
    if len(error_df) > 0:
        raise ValueError(f"There are {len(error_df)} rows with logical OHLC errors")

    # ==============================
    # 7️⃣ Remove duplicate index (Date)
    # ==============================
    if remove_duplicates:
        df = df[~df.index.duplicated(keep="first")]
    else:
        finddup = df[df.index.duplicated(keep=False)]
        if len(finddup):
            raise ValueError(f"There are {len(finddup)} rows with duplicate index")

    # ==============================
    # 8️⃣ Sort by index
    # ==============================
    if sort_by_index:
        df = df.sort_index()

    # Fix structure
    # Ngay xua du lieu lich su co row cua 11h30 va 14h30, hien thi khong co 
    # Can chuan hoa lai du lieu bang cach cong don du lieu cu, sau do xoa row 11h30 va 14h30
    # Tuy nhien cach do phuc tap nen hien tai cu xoa 2 row nay di
    tmp_df = df.copy()
    tmp_df['time_int'] = tmp_df.index.hour * 100 + tmp_df.index.minute
    df = tmp_df[(tmp_df['time_int'] != 1130) & (tmp_df['time_int'] != 1430)]
    df = df.drop(columns=['time_int'])

    return df