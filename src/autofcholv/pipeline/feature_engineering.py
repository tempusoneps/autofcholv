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
from autofcholv.pipeline.features.kmeans import extract_features as extract_kmeans_features
from autofcholv.pipeline.features.hdbscan import extract_features as extract_hdbscan_features
from autofcholv.pipeline.features.gmm import extract_features as extract_gmm_features
from autofcholv.pipeline.features.dbscan import extract_features as extract_dbscan_features
from autofcholv.pipeline.features.agglomerative import extract_features as extract_agglomerative_features
from autofcholv.pipeline.features.birch import extract_features as extract_birch_features
from autofcholv.pipeline.features.optics import extract_features as extract_optics_features
from autofcholv.pipeline.features.spectral import extract_features as extract_spectral_features
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
    ("kmeans_features", extract_kmeans_features),
    ("hdbscan_features", extract_hdbscan_features),
    ("gmm_features", extract_gmm_features),
    ("dbscan_features", extract_dbscan_features),
    ("agglomerative_features", extract_agglomerative_features),
    ("birch_features", extract_birch_features),
    ("optics_features", extract_optics_features),
    ("spectral_features", extract_spectral_features),
]


def get_feature_steps(config: Config | None = None) -> list[tuple[str, Callable]]:
    """Return active feature extraction steps filtered by config.disable_modules."""
    if config is None:
        return list(FEATURE_STEPS)

    raw_disabled = getattr(config, "disable_modules", None)
    if not raw_disabled:
        return list(FEATURE_STEPS)

    disabled = set()
    if isinstance(raw_disabled, dict):
        for k, v in raw_disabled.items():
            if v:
                disabled.add(str(k).strip().lower())
    elif isinstance(raw_disabled, (list, tuple, set)):
        for item in raw_disabled:
            disabled.add(str(item).strip().lower())
    elif isinstance(raw_disabled, str):
        for item in raw_disabled.split(","):
            if item.strip():
                disabled.add(item.strip().lower())

    active_steps = []
    for name, func in FEATURE_STEPS:
        base_name = name[:-9] if name.endswith("_features") else name
        if name.lower() in disabled or base_name.lower() in disabled:
            continue
        active_steps.append((name, func))

    return active_steps


@timing
def build_features(
    df: pd.DataFrame,
    config: Config,
    progress_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    steps = get_feature_steps(config)
    for name, func in steps:
        with timeit(name):
            df = func(df, config).copy()
        if progress_callback:
            progress_callback(name)
            
    # Drop all columns starting with _temp_
    temp_cols = [col for col in df.columns if col.startswith("_temp_")]
    if temp_cols:
        df = df.drop(columns=temp_cols)
        
    return df
