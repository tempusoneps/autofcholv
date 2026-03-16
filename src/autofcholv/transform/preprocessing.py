import pandas as pd
from sklearn.preprocessing import LabelEncoder


DROP_COLUMNS = ['time_d', 'couple_cs_1st_cond', 'couple_cs_2rd_cond']


def preprocessing_data(df):
    df.drop(columns=DROP_COLUMNS, inplace=True)
    df.dropna(inplace=True)
    return df


def safe_int_convert(series):
    le = LabelEncoder()
    to_series = le.fit_transform(series)
    return to_series

def numeric_data(df):
    df = df.apply(lambda col: safe_int_convert(col) if col.dtype == "object" else col)
    return df
    