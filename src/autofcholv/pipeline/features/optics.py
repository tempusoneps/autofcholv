from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_OPTICS_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "optics_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "min_samples": 20,
    },
    "optics_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "min_samples": 20,
    },
    "optics_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "min_samples": 15,
    },
    "optics_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "min_samples": 20,
    },
    "optics_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "min_samples": 20,
    },
    "optics_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "min_samples": 20,
    },
    "optics_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "min_samples": 25,
    },
    "optics_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "min_samples": 20,
    },
    "optics_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "min_samples": 25,
    },
    "optics_macro_risk_regime": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "min_samples": 25,
    },
}


def run_optics_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Run OPTICS density reachability clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'min_samples': Number of samples in a neighborhood for a point to be considered as a core point (default: 20).
            - 'max_eps': Maximum distance between two samples for one to be considered in neighborhood (default: np.inf).
            - 'metric': Metric used for distance computation (default: 'euclidean').

    Returns:
        DataFrame with new cluster columns added (noise labeled as -1).
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_OPTICS_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for OPTICS clustering '{cluster_col}': {missing}")

        min_samples = int(cluster_cfg.get("min_samples", 20))
        max_eps = float(cluster_cfg.get("max_eps", np.inf))
        metric = str(cluster_cfg.get("metric", "euclidean"))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= min_samples and min_samples > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            optics = OPTICS(min_samples=min_samples, max_eps=max_eps, metric=metric)
            cluster_series.loc[valid_mask] = optics.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "optics_clusters", None) or DEFAULT_OPTICS_CLUSTERS
    return run_optics_clustering(df, clusters_config=clusters)
