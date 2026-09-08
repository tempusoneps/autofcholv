from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_DBSCAN_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "dbscan_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "eps": 0.5,
        "min_samples": 5,
    },
    "dbscan_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "eps": 0.5,
        "min_samples": 5,
    },
    "dbscan_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "eps": 0.5,
        "min_samples": 5,
    },
    "dbscan_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "eps": 0.6,
        "min_samples": 5,
    },
    "dbscan_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "eps": 0.7,
        "min_samples": 5,
    },
    "dbscan_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "eps": 0.7,
        "min_samples": 5,
    },
    "dbscan_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "eps": 0.8,
        "min_samples": 5,
    },
    "dbscan_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "eps": 0.6,
        "min_samples": 5,
    },
    "dbscan_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "eps": 0.8,
        "min_samples": 5,
    },
    "dbscan_macro_risk_regime": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "eps": 0.8,
        "min_samples": 5,
    },
}


def run_dbscan_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Run DBSCAN density-based clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'eps': Maximum distance between two samples for one to be considered as in the neighborhood (default: 0.5).
            - 'min_samples': Number of samples in a neighborhood for a point to be considered a core point (default: 5).
            - 'metric': Distance metric (default: 'euclidean').

    Returns:
        DataFrame with new cluster columns added (noise labeled as -1).
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_DBSCAN_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for DBSCAN clustering '{cluster_col}': {missing}")

        eps = float(cluster_cfg.get("eps", 0.5))
        min_samples = int(cluster_cfg.get("min_samples", 5))
        metric = str(cluster_cfg.get("metric", "euclidean"))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= min_samples and min_samples > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
            cluster_series.loc[valid_mask] = db.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "dbscan_clusters", None) or DEFAULT_DBSCAN_CLUSTERS
    return run_dbscan_clustering(df, clusters_config=clusters)
