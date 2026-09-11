import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Optional, get_args, get_origin


@dataclass(frozen=True)
class Config:
    selected_time_frame: str = "5m"
    one_day_bars: int = 49
    one_hour_bars: int = 12
    one_week_bars: int = 245
    morning_bars: int = 30
    afternoon_bars: int = 19
    micro_lookback: int = 5
    short_lookback: int = 10
    medium_lookback: int = 20
    long_lookback: int = 50
    macro_lookback: int = 100
    momentum_lookback: int = 24
    volatility_lookback: int = 24
    volume_lookback: int = 24
    fast_trend_lookback: int = 24
    slow_trend_lookback: int = 245
    ibs_lookback: int = 5
    drop_first_rows: int = 245
    classic_indicators: Dict[str, Any] = field(
        default_factory=lambda: {
            "RSI": 14,
            "STOCHRSI": 14,
            "MACD": [12, 26, 9],
            "PPO": [12, 26, 9],
            "WILLIAMS_R": 14,
            "AO": [5, 34],
            "UO": [7, 14, 28],
            "MFI": 14,
            "SUPERTREND": [10, 3.0],
            "TRIX": [15, 9],
            "ADX": 14,
            "CHOP": 14,
            "CONNORS_RSI": [3, 2],
        }
    )
    ema_windows: list[int] = field(default_factory=lambda: [8, 20, 21, 55, 250])
    kmeans_clusters: Dict[str, Any] = field(
        default_factory=lambda: {
            "cluster_kmeans_001": {
                "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
                "n_clusters": 4,
            },
            "cluster_kmeans_002": {
                "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
                "n_clusters": 4,
            },
            "cluster_kmeans_003": {
                "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
                "n_clusters": 5,
            },
            "cluster_kmeans_004": {
                "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
                "n_clusters": 4,
            },
            "cluster_kmeans_005": {
                "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
                "n_clusters": 4,
            },
            "cluster_kmeans_006": {
                "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
                "n_clusters": 4,
            },
            "cluster_kmeans_007": {
                "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
                "n_clusters": 4,
            },
            "cluster_kmeans_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "n_clusters": 4,
            },
            "cluster_kmeans_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "n_clusters": 5,
            },
            "cluster_kmeans_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "n_clusters": 5,
            },
        }
    )
    hdbscan_clusters: Dict[str, Any] = field(
        default_factory=lambda: {
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
    )
    gmm_clusters: Dict[str, Any] = field(
        default_factory=lambda: {
            "cluster_gmm_001": {
                "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_002": {
                "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_003": {
                "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
                "n_components": 5,
                "covariance_type": "full",
            },
            "cluster_gmm_004": {
                "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_005": {
                "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_006": {
                "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_007": {
                "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "n_components": 4,
                "covariance_type": "full",
            },
            "cluster_gmm_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "n_components": 5,
                "covariance_type": "full",
            },
            "cluster_gmm_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "n_components": 5,
                "covariance_type": "full",
            },
        }
    )
    dbscan_clusters: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "cluster_dbscan_001": {
                "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
                "eps": 0.5,
                "min_samples": 5,
            },
            "cluster_dbscan_002": {
                "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
                "eps": 0.5,
                "min_samples": 5,
            },
            "cluster_dbscan_003": {
                "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
                "eps": 0.5,
                "min_samples": 5,
            },
            "cluster_dbscan_004": {
                "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
                "eps": 0.6,
                "min_samples": 5,
            },
            "cluster_dbscan_005": {
                "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
                "eps": 0.7,
                "min_samples": 5,
            },
            "cluster_dbscan_006": {
                "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
                "eps": 0.7,
                "min_samples": 5,
            },
            "cluster_dbscan_007": {
                "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
                "eps": 0.8,
                "min_samples": 5,
            },
            "cluster_dbscan_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "eps": 0.6,
                "min_samples": 5,
            },
            "cluster_dbscan_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "eps": 0.8,
                "min_samples": 5,
            },
            "cluster_dbscan_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "eps": 0.8,
                "min_samples": 5,
            },
        }
    )
    agglomerative_clusters: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "cluster_agglomerative_001": {
                "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_002": {
                "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_003": {
                "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
                "n_clusters": 5,
                "linkage": "ward",
            },
            "cluster_agglomerative_004": {
                "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_005": {
                "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_006": {
                "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_007": {
                "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "n_clusters": 4,
                "linkage": "ward",
            },
            "cluster_agglomerative_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "n_clusters": 5,
                "linkage": "ward",
            },
            "cluster_agglomerative_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "n_clusters": 5,
                "linkage": "ward",
            },
        }
    )
    birch_clusters: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "cluster_birch_001": {
                "features": ["adx_14", "atr_pct_medium", "volume_ratio"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_002": {
                "features": ["return_medium", "volume_ratio", "volume_zscore", "mfi_standard"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_003": {
                "features": ["body_rate", "upwick_rate", "lowwick_rate", "body_abs", "ibs"],
                "n_clusters": 5,
                "threshold": 0.5,
            },
            "cluster_birch_004": {
                "features": ["return_micro", "return_short", "return_medium", "rsi_medium", "stochrsi_k"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_005": {
                "features": ["bb_width", "atr_pct_medium", "realized_volatility", "pac_position", "pac_width_bias", "env_position"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_006": {
                "features": ["adx_14", "adxr", "aroon_osc", "dmp_14", "rsi_slope_medium", "close_zscore"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_007": {
                "features": ["amihud", "market_placement", "path_liquidity", "spread_proxy", "volume_zscore", "volume_up_ratio", "volume_down_ratio"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "n_clusters": 4,
                "threshold": 0.5,
            },
            "cluster_birch_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "n_clusters": 5,
                "threshold": 0.5,
            },
            "cluster_birch_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "n_clusters": 5,
                "threshold": 0.5,
            },
        }
    )
    optics_clusters: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
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
                "min_samples": 20,
            },
            "cluster_optics_008": {
                "features": ["close_to_vwap", "vwap_bias", "close_zscore", "ibs", "env_position"],
                "min_samples": 20,
            },
            "cluster_optics_009": {
                "features": ["return_short", "body_rate", "volume_ratio", "volume_zscore", "force_ratio", "mfi_standard", "upwick_rate"],
                "min_samples": 20,
            },
            "cluster_optics_010": {
                "features": ["return_long", "return_medium", "atr_pct_long", "realized_volatility", "chaikin_volatility", "adx_14", "close_to_vwap"],
                "min_samples": 20,
            },
        }
    )
    spectral_clusters: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
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
    )
    disable_modules: list[str] = field(default_factory=list)


CONFIG_FIELD_NAMES = {field_name for field_name in Config.__dataclass_fields__}
CONFIG_KEY_ALIASES = {
    "SELECTED_TIME_FRAME": "selected_time_frame",
    "ONE_DAY_BARS": "one_day_bars",
    "ONE_HOUR_BARS": "one_hour_bars",
    "ONE_WEEK_BARS": "one_week_bars",
    "MORNING_BARS": "morning_bars",
    "AFTERNOON_BARS": "afternoon_bars",
    "MICRO_LOOKBACK": "micro_lookback",
    "SHORT_LOOKBACK": "short_lookback",
    "MEDIUM_LOOKBACK": "medium_lookback",
    "LONG_LOOKBACK": "long_lookback",
    "MACRO_LOOKBACK": "macro_lookback",
    "MOMENTUM_LOOKBACK": "momentum_lookback",
    "VOLATILITY_LOOKBACK": "volatility_lookback",
    "VOLUME_LOOKBACK": "volume_lookback",
    "FAST_TREND_LOOKBACK": "fast_trend_lookback",
    "SLOW_TREND_LOOKBACK": "slow_trend_lookback",
    "IBS_LOOKBACK": "ibs_lookback",
    "DROP_FIRST_ROWS": "drop_first_rows",
    "CLASSIC_INDICATORS": "classic_indicators",
    "EMA_WINDOWS": "ema_windows",
    "KMEANS_CLUSTERS": "kmeans_clusters",
    "HDBSCAN_CLUSTERS": "hdbscan_clusters",
    "GMM_CLUSTERS": "gmm_clusters",
    "DBSCAN_CLUSTERS": "dbscan_clusters",
    "AGGLOMERATIVE_CLUSTERS": "agglomerative_clusters",
    "BIRCH_CLUSTERS": "birch_clusters",
    "OPTICS_CLUSTERS": "optics_clusters",
    "SPECTRAL_CLUSTERS": "spectral_clusters",
    "DISABLE _MODULES": "disable_modules",
    "DISABLE_MODULES": "disable_modules",
}
FIELD_TO_CONFIG_KEY = {field: key for key, field in CONFIG_KEY_ALIASES.items()}
DEFAULT_CONFIG = {
    FIELD_TO_CONFIG_KEY[field_name]: value
    for field_name, value in asdict(Config()).items()
}

DEFAULT_CONFIG_FILENAME = "config.default.json"
PACKAGE_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / DEFAULT_CONFIG_FILENAME


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load config from JSON/YAML file, or default config file (config.default.json), or built-in defaults.
    """
    if config_file:
        return _load_from_file(config_file)

    local_default = Path(DEFAULT_CONFIG_FILENAME)
    if local_default.exists() and local_default.is_file():
        return _load_from_file(str(local_default))

    if PACKAGE_DEFAULT_CONFIG_PATH.exists() and PACKAGE_DEFAULT_CONFIG_PATH.is_file():
        return _load_from_file(str(PACKAGE_DEFAULT_CONFIG_PATH))

    return Config()

def generate_default_config_file(path: Optional[str] = None) -> bool:
    if not path:
        path = "config.json"
    
    file_path = Path(path)
    
    try:
        if file_path.suffix.lower() == ".json":
            config = dict(DEFAULT_CONFIG)
            if file_path.exists():
                existing_config = json.loads(file_path.read_text(encoding="utf-8"))
                config.update(existing_config)
            file_path.write_text(
                json.dumps(config, indent=2) + "\n",
                encoding="utf-8",
            )
            return True

        raise ValueError("Default config generation only supports .json files")
    except Exception as e:
        print(f"Error generating config file: {e}")
        return False


def _load_from_file(path: Optional[str]) -> Config:
    if not path:
        return Config()

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = file_path.suffix.lower()

    if suffix == ".json":
        config = json.loads(file_path.read_text())
        return _config_from_mapping(config)

    if suffix in [".yaml", ".yml"]:
        import yaml
        config = yaml.safe_load(file_path.read_text())
        return _config_from_mapping(config or {})

    raise ValueError(f"Unsupported config file format: {file_path.suffix}")


def _config_from_mapping(config: Dict[str, Any]) -> Config:
    values = asdict(Config())
    config_fields = {field.name: field for field in fields(Config)}
    for key, value in config.items():
        field_name = CONFIG_KEY_ALIASES.get(key, key)
        if field_name in CONFIG_FIELD_NAMES:
            values[field_name] = _coerce_config_value(value, config_fields[field_name].type)
    return Config(**values)


def _coerce_config_value(value: Any, field_type: Any) -> Any:
    if field_type is int:
        return int(value)
    if field_type is str:
        return str(value)
    if get_origin(field_type) in (list, tuple) or field_type is list:
        args = get_args(field_type)
        elem_type = args[0] if args else int
        if isinstance(value, str):
            value = [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, dict):
            value = [k for k, v in value.items() if v]
        elif isinstance(value, (set, tuple)):
            value = list(value)
        if isinstance(value, list):
            if elem_type is str:
                return [str(item).strip() for item in value if str(item).strip()]
            if elem_type is int:
                return [int(item) for item in value]
            return value
        return value
    return value


def ensure_config(config: Optional[Config] = None) -> Config:
    return config if config is not None else Config()
