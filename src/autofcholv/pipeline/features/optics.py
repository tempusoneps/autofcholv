import warnings
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_OPTICS_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "cluster_optics_001": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "min_samples": 20,
    },
    "cluster_optics_002": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "min_samples": 20,
    },
    "cluster_optics_003": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "min_samples": 15,
    },
    "cluster_optics_004": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "min_samples": 20,
    },
    "cluster_optics_005": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "min_samples": 20,
    },
    "cluster_optics_006": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "min_samples": 20,
    },
    "cluster_optics_007": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "min_samples": 25,
    },
    "cluster_optics_008": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "min_samples": 20,
    },
    "cluster_optics_009": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "min_samples": 25,
    },
    "cluster_optics_010": {
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
        max_train_samples = int(cluster_cfg.get("max_train_samples", 5000))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= min_samples and min_samples > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*divide by zero.*")
                if n_valid > max_train_samples and max_train_samples > min_samples:
                    # Subsample evenly across the time series to avoid O(N^2) memory and runtime explosion
                    sample_idx = np.linspace(0, n_valid - 1, max_train_samples, dtype=int)
                    train_data = scaled_features[sample_idx]
                    optics = OPTICS(min_samples=min_samples, max_eps=max_eps, metric=metric)
                    sample_labels = optics.fit_predict(train_data)

                    from sklearn.neighbors import KNeighborsClassifier
                    knn = KNeighborsClassifier(n_neighbors=1)
                    knn.fit(train_data, sample_labels)
                    cluster_series.loc[valid_mask] = knn.predict(scaled_features).astype("int32")
                else:
                    optics = OPTICS(min_samples=min_samples, max_eps=max_eps, metric=metric)
                    cluster_series.loc[valid_mask] = optics.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "optics_clusters", None) or DEFAULT_OPTICS_CLUSTERS
    return run_optics_clustering(df, clusters_config=clusters)
