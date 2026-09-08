from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from autofcholv.config.config import Config

DEFAULT_GMM_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "gmm_regime_core": {
        "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_price_volume_anatomy": {
        "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_candle_shape_rejection": {
        "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
        "n_components": 5,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_multi_horizon_momentum": {
        "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_breakout_volatility_squeeze": {
        "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_trend_exhaustion_divergence": {
        "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_market_microstructure": {
        "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_mean_reversion_extremes": {
        "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
        "n_components": 4,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_order_flow_impulse": {
        "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
        "n_components": 5,
        "covariance_type": "full",
        "random_state": 42,
    },
    "gmm_macro_risk_regime": {
        "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
        "n_components": 5,
        "covariance_type": "full",
        "random_state": 42,
    },
}


def run_gmm_clustering(
    df: pd.DataFrame,
    clusters_config: Optional[Dict[str, Any]] = None,
    default_random_state: int = 42,
) -> pd.DataFrame:
    """Run Gaussian Mixture Models clustering on specified feature groups and append cluster label columns.

    Args:
        df: Input DataFrame with extracted features.
        clusters_config: Mapping from cluster column name to config dict containing:
            - 'features': List of column names to cluster on.
            - 'n_components' (or 'k'): Number of mixture components (default: 3).
            - 'covariance_type': String ('full', 'tied', 'diag', 'spherical', default: 'full').
            - 'random_state': Optional random state for reproducibility.
            - 'reg_covar': Regularization added to covariance diagonal (default: 1e-6).
        default_random_state: Fallback random seed when not set per cluster.

    Returns:
        DataFrame with new GMM cluster columns added (invalid/warmup labeled as -1).
    """
    config_dict = clusters_config if clusters_config is not None else DEFAULT_GMM_CLUSTERS

    for cluster_col, cluster_cfg in config_dict.items():
        features = cluster_cfg.get("features", [])
        if not features:
            continue

        missing = [col for col in features if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns for GMM clustering '{cluster_col}': {missing}")

        n_components = int(cluster_cfg.get("n_components") or cluster_cfg.get("k", 3))
        covariance_type = str(cluster_cfg.get("covariance_type", "full"))
        random_state = int(cluster_cfg.get("random_state", default_random_state))
        reg_covar = float(cluster_cfg.get("reg_covar", 1e-6))

        sub_df = df[features]
        valid_mask = sub_df.notna().all(axis=1) & np.isfinite(sub_df).all(axis=1)
        n_valid = int(valid_mask.sum())

        cluster_series = pd.Series(-1, index=df.index, dtype="int32")
        if n_valid >= n_components and n_components > 1:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(sub_df.loc[valid_mask])
            gmm = GaussianMixture(
                n_components=n_components,
                covariance_type=covariance_type,
                random_state=random_state,
                reg_covar=reg_covar,
            )
            cluster_series.loc[valid_mask] = gmm.fit_predict(scaled_features).astype("int32")

        df[cluster_col] = cluster_series

    return df


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Feature extraction entry point for the autofcholv pipeline."""
    clusters = getattr(config, "gmm_clusters", None) or DEFAULT_GMM_CLUSTERS
    return run_gmm_clustering(df, clusters_config=clusters)
