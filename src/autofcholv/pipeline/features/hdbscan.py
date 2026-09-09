from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_HDBSCAN_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "cluster_hdbscan_001": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "min_cluster_size": 15,
        "min_samples": 5,
    },
    "cluster_hdbscan_002": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
    "cluster_hdbscan_003": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "min_cluster_size": 15,
        "min_samples": 5,
    },
    "cluster_hdbscan_004": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
    "cluster_hdbscan_005": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "min_cluster_size": 15,
        "min_samples": 5,
    },
    "cluster_hdbscan_006": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
    "cluster_hdbscan_007": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
    "cluster_hdbscan_008": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "min_cluster_size": 15,
        "min_samples": 5,
    },
    "cluster_hdbscan_009": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
    "cluster_hdbscan_010": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "min_cluster_size": 20,
        "min_samples": 5,
    },
}


def run_hdbscan_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Run HDBSCAN density-based clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'min_cluster_size': Minimum size of clusters (default: 15).
            - 'min_samples': Number of samples in a neighborhood for a point to be considered a core point (default: None).
            - 'cluster_selection_epsilon': Distance threshold for cluster flat merging (default: 0.0).
            - 'metric': Distance metric (default: 'euclidean').

    Returns:
        DataFrame with new cluster columns added (noise labeled as -1).
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_HDBSCAN_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for HDBSCAN clustering '{cluster_col}': {missing}")

        min_cluster_size = int(cluster_cfg.get("min_cluster_size", 15))
        min_samples = cluster_cfg.get("min_samples")
        if min_samples is not None:
            min_samples = int(min_samples)
        cluster_selection_epsilon = float(cluster_cfg.get("cluster_selection_epsilon", 0.0))
        metric = str(cluster_cfg.get("metric", "euclidean"))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= min_cluster_size and min_cluster_size > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            hdb = HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                cluster_selection_epsilon=cluster_selection_epsilon,
                metric=metric,
                copy=True,
            )
            cluster_series.loc[valid_mask] = hdb.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "hdbscan_clusters", None) or DEFAULT_HDBSCAN_CLUSTERS
    return run_hdbscan_clustering(df, clusters_config=clusters)
