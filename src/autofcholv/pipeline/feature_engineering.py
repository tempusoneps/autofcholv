import pandas as pd
from typing import Callable
from autofcholv.config.config import Config
from autofcholv.pipeline.features.close import extract_features as extract_close_features
from autofcholv.pipeline.features.mix import extract_features as extract_mix_features
from autofcholv.pipeline.features.price import extract_features as extract_price_features
from autofcholv.pipeline.features.time import extract_features as extract_time_features
from autofcholv.pipeline.features.trend import extract_features as extract_trend_features
from autofcholv.pipeline.features.volatility import extract_features as extract_volatility_features
from autofcholv.pipeline.features.resample import extract_features as extract_resample_features
from autofcholv.pipeline.features.candlestick import extract_features as extract_candlestick_features
from autofcholv.pipeline.features.lag import extract_features as extract_lag_features
from autofcholv.pipeline.features.liquidity import extract_features as extract_liquidity_features
from autofcholv.pipeline.features.group import extract_features as extract_group_features
from autofcholv.pipeline.features.signal import extract_features as extract_signal_features
from autofcholv.pipeline.features.strategy import extract_features as extract_strategy_features
from autofcholv.pipeline.features.volume import extract_features as extract_volume_features
from autofcholv.utils.timing import timing, timeit

FEATURE_STEPS = [
    ("time_features", extract_time_features),
    ("resample_features", extract_resample_features),
    ("candlestick_features", extract_candlestick_features),
    ("close_features", extract_close_features),
    ("price_features", extract_price_features),
    ("trend_features", extract_trend_features),
    ("volatility_features", extract_volatility_features),
    ("volume_features", extract_volume_features),
    ("liquidity_features", extract_liquidity_features),
    ("lag_features", extract_lag_features),
    ("mix_features", extract_mix_features),
    ("group_features", extract_group_features),
    ("signal_features", extract_signal_features),
    ("strategy_features", extract_strategy_features),
]


@timing
def build_features(
    df: pd.DataFrame,
    config: Config,
    progress_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    for name, func in FEATURE_STEPS:
        with timeit(name):
            df = func(df, config).copy()
        if progress_callback:
            progress_callback(name)
            
    # Drop all columns starting with _temp_
    temp_cols = [col for col in df.columns if col.startswith("_temp_")]
    if temp_cols:
        df = df.drop(columns=temp_cols)
        
    return df
