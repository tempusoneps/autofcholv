import os
import pytest
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def load_test_env():
    """Load env vars from .env.example into the environment for testing."""
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env.example")
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        # Fallback values if file missing
        os.environ["SELECTED_TIME_FRAME"] = "5m"
        os.environ["OLD_1DAY_BARS"] = "51"
        os.environ["ONE_DAY_BARS"] = "49"
        os.environ["ONE_HOUR_BARS"] = "12"
        os.environ["ONE_WEEK_BARS"] = "245"
        os.environ["MORNING_BARS"] = "30"
        os.environ["AFTERNOON_BARS"] = "19"
        os.environ["MOMENTUM_LOOKBACK"] = "24"
        os.environ["VOLATILITY_LOOKBACK"] = "24"
        os.environ["VOLUME_LOOKBACK"] = "24"
        os.environ["FAST_TREND_LOOKBACK"] = "24"
        os.environ["LOW_TREND_LOOKBACK"] = "245"
        os.environ["IBS_LOOKBACK"] = "5"
