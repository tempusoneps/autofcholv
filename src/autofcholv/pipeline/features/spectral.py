from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_SPECTRAL_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "spectral_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "n_clusters": 5,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "n_clusters": 4,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "n_clusters": 5,
        "affinity": "rbf",
        "random_state": 42,
    },
    "spectral_macro_risk_regime": {
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

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= k and k > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
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
