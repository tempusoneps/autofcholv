from autofcholv.pipeline.features.close import extract_features as extract_close_features
from autofcholv.pipeline.features.mix import extract_features as extract_mix_features
from autofcholv.pipeline.features.time import extract_features as extract_time_features
from autofcholv.pipeline.features.resample import extract_features as extract_resample_features
from autofcholv.pipeline.features.candlestick import extract_features as extract_candlestick_features


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df = extract_time_features(df)
    df = extract_resample_features(df)
    df = extract_candlestick_features(df)
    df = extract_close_features(df)
    df = extract_mix_features(df)
    return df