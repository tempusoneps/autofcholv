from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_AGGLOMERATIVE_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "agglomerative_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "n_clusters": 5,
        "linkage": "ward",
    },
    "agglomerative_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "n_clusters": 4,
        "linkage": "ward",
    },
    "agglomerative_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "n_clusters": 5,
        "linkage": "ward",
    },
    "agglomerative_macro_risk_regime": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "n_clusters": 5,
        "linkage": "ward",
    },
}


def run_agglomerative_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Run Agglomerative Hierarchical clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'n_clusters' (or 'k'): Number of clusters (default: 4).
            - 'linkage': Linkage criterion ('ward', 'complete', 'average', 'single', default: 'ward').
            - 'metric': Metric used to compute the linkage (default: 'euclidean').

    Returns:
        DataFrame with new cluster columns added.
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_AGGLOMERATIVE_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for Agglomerative clustering '{cluster_col}': {missing}")

        k = int(cluster_cfg.get("n_clusters") or cluster_cfg.get("k", 4))
        linkage = str(cluster_cfg.get("linkage", "ward"))
        metric = str(cluster_cfg.get("metric", "euclidean"))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= k and k > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            agg = AgglomerativeClustering(n_clusters=k, linkage=linkage, metric=metric)
            cluster_series.loc[valid_mask] = agg.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "agglomerative_clusters", None) or DEFAULT_AGGLOMERATIVE_CLUSTERS
    return run_agglomerative_clustering(df, clusters_config=clusters)
