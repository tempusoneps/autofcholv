import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "SELECTED_TIME_FRAME": "5m",
    "OLD_1DAY_BARS": "51",
    "ONE_DAY_BARS": "49",
    "ONE_HOUR_BARS": "12",
    "ONE_WEEK_BARS": "245",
    "MORNING_BARS": "30",
    "AFTERNOON_BARS": "19",
    "MOMENTUM_LOOKBACK": "24",
    "VOLATILITY_LOOKBACK": "24",
    "VOLUME_LOOKBACK": "24",
    "FAST_TREND_LOOKBACK": "24",
    "LOW_TREND_LOOKBACK": "245",
    "IBS_LOOKBACK": "5",
    "DROP_FIRST_ROWS": "245",
}

def load_config(
    config_file: Optional[str] = None
) -> None:
    """
    Load config with priority:
    1. env
    2. file
    3. defaults
    """

    # 1. env
    is_success = _load_from_env()
    if is_success:
        return 

    # 2. file
    is_success = _load_from_file(config_file)
    if is_success:
        return 
    # 3. defaults
    is_success = _load_from_defaults()
    if is_success:
        return

def generate_default_config_file(path: Optional[str] = None) -> bool:
    if not path:
        path = ".env"
    
    file_path = Path(path)
    existing_keys = set()
    
    try:
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key = line.split("=", 1)[0].strip()
                        existing_keys.add(key)
        
        with file_path.open("a" if file_path.exists() else "w", encoding="utf-8") as f:
            for key, value in DEFAULT_CONFIG.items():
                if key not in existing_keys:
                    f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        print(f"Error generating config file: {e}")
        return False


def _load_from_file(path: Optional[str]) -> bool:
    if not path:
        return False

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    if file_path.suffix in [".json"]:
        config = json.loads(file_path.read_text())
        return _update_config(config)

    elif file_path.suffix in [".yaml", ".yml"]:
        import yaml
        config = yaml.safe_load(file_path.read_text())
        return _update_config(config)
    return False


def _update_config(config: Dict[str, Any]) -> bool:
    for key, value in DEFAULT_CONFIG.items():
        os.environ[key] = config.get(key, value)
    return True

def _load_from_env() -> bool:
    for key, value in DEFAULT_CONFIG.items():
        if not os.getenv(key):
            return False
    return True


def _load_from_defaults() -> bool:
    for key, value in DEFAULT_CONFIG.items():
        os.environ[key] = value
    return True
