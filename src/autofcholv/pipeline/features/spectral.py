from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_SPECTRAL_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "cluster_spectral_001": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_002": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_003": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "n_clusters": 5,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_004": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_005": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_006": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_007": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_008": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_009": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "n_clusters": 5,
        "affinity": "rbf",
        "random_state": 42,
    },
    "cluster_spectral_010": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "n_clusters": 5,
        "affinity": "rbf",
        "random_state": 42,
    },
}


def run_spectral_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
    default_random_state: int = 42,
) -> pd.DataFrame:
    """Run Spectral Clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'n_clusters' (or 'k'): Number of clusters (default: 4).
            - 'affinity': Affinity metric ('rbf', 'nearest_neighbors', default: 'rbf').
            - 'random_state': Optional random state for reproducibility.
        default_random_state: Fallback random seed.

    Returns:
        DataFrame with new cluster columns added.
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_SPECTRAL_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for Spectral clustering '{cluster_col}': {missing}")

        k = int(cluster_cfg.get("n_clusters") or cluster_cfg.get("k", 4))
        affinity = str(cluster_cfg.get("affinity", "rbf"))
        random_state = int(cluster_cfg.get("random_state", default_random_state))
        max_train_samples = int(cluster_cfg.get("max_train_samples", 5000))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= k and k > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            if n_valid > max_train_samples and max_train_samples > k:
                # Subsample evenly across the time series to avoid O(N^2) memory explosion
                sample_idx = np.linspace(0, n_valid - 1, max_train_samples, dtype=int)
                train_data = scaled_features[sample_idx]
                sc = SpectralClustering(
                    n_clusters=k,
                    affinity=affinity,
                    random_state=random_state,
                    assign_labels="kmeans",
                    n_init=1,
                )
                sample_labels = sc.fit_predict(train_data)

                # Compute cluster centroids
                centroids = np.zeros((k, train_data.shape[1]), dtype=scaled_features.dtype)
                for cluster_id in range(k):
                    c_mask = sample_labels == cluster_id
                    if np.any(c_mask):
                        centroids[cluster_id] = train_data[c_mask].mean(axis=0)

                # Assign all points to nearest cluster centroid
                dists = np.linalg.norm(scaled_features[:, None, :] - centroids[None, :, :], axis=2)
                cluster_series.loc[valid_mask] = np.argmin(dists, axis=1).astype("int32")
            else:
                sc = SpectralClustering(
                    n_clusters=k,
                    affinity=affinity,
                    random_state=random_state,
                    assign_labels="kmeans",
                    n_init=1,
                )
                cluster_series.loc[valid_mask] = sc.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "spectral_clusters", None) or DEFAULT_SPECTRAL_CLUSTERS
    return run_spectral_clustering(df, clusters_config=clusters)
