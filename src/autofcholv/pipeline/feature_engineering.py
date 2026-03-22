import pandas as pd
from autofcholv.pipeline.features.close import extract_features as extract_close_features
from autofcholv.pipeline.features.mix import extract_features as extract_mix_features
from autofcholv.pipeline.features.time import extract_features as extract_time_features
from autofcholv.pipeline.features.resample import extract_features as extract_resample_features
from autofcholv.pipeline.features.candlestick import extract_features as extract_candlestick_features
from autofcholv.pipeline.features.lag import extract_features as extract_lag_features
from autofcholv.pipeline.features.group import extract_features as extract_group_features
from autofcholv.pipeline.features.signal import extract_features as extract_signal_features
from autofcholv.pipeline.features.volume import extract_features as extract_volume_features
from autofcholv.utils.timing import timing, timeit


@timing
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    steps = [
        ("time_features", extract_time_features),
        ("resample_features", extract_resample_features),
        ("candlestick_features", extract_candlestick_features),
        ("close_features", extract_close_features),
        ("volume_features", extract_volume_features),
        ("lag_features", extract_lag_features),
        ("mix_features", extract_mix_features),
        ("group_features", extract_group_features),
        ("signal_features", extract_signal_features),
    ]
    for name, func in steps:
        with timeit(name):
            df = func(df)
    return df
