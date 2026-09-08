from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import Birch
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_BIRCH_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "birch_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "n_clusters": 5,
        "threshold": 0.5,
    },
    "birch_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "n_clusters": 4,
        "threshold": 0.5,
    },
    "birch_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "n_clusters": 5,
        "threshold": 0.5,
    },
    "birch_macro_risk_regime": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "n_clusters": 5,
        "threshold": 0.5,
    },
}


def run_birch_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Run BIRCH CF-Tree clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'n_clusters' (or 'k'): Number of clusters (default: 4).
            - 'threshold': Radius of the subcluster obtained by merging a new sample (default: 0.5).
            - 'branching_factor': Maximum number of CF subclusters in each node (default: 50).

    Returns:
        DataFrame with new cluster columns added.
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_BIRCH_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for BIRCH clustering '{cluster_col}': {missing}")

        k = int(cluster_cfg.get("n_clusters") or cluster_cfg.get("k", 4))
        threshold = float(cluster_cfg.get("threshold", 0.5))
        branching_factor = int(cluster_cfg.get("branching_factor", 50))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= k and k > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            birch = Birch(n_clusters=k, threshold=threshold, branching_factor=branching_factor)
            cluster_series.loc[valid_mask] = birch.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "birch_clusters", None) or DEFAULT_BIRCH_CLUSTERS
    return run_birch_clustering(df, clusters_config=clusters)
