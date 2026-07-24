import os
from datetime import datetime, timezone
from pathlib import Path

import yaml


def load_config():
    CONFIG_PATH = os.environ.get(
        "CONFIG_PATH", str(Path(__file__).parent.parent / "config.yaml")
    )

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


CONFIG = load_config()


RAW_DIR = Path(CONFIG["paths"]["raw_dir"])
RAW_DIR.mkdir(parents=True, exist_ok=True)

DUCKDB_PATH = Path(CONFIG["paths"]["duckdb_path"])
DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)


assert CONFIG["requests"]["api_url"].startswith("http"), "api_url must be a full URL"

assert CONFIG["requests"]["max_retries"] > 0
assert CONFIG["requests"]["request_timeout"] > 0


def dt_check_utc_aligned(dt_str: str) -> datetime:
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError(
            f"'{dt_str}' must be UTC with 0 offset (ISO string ending in Z)"
        )
    if dt.minute != 0 or dt.second != 0 or dt.microsecond != 0:
        raise ValueError(
            f"'{dt_str}' must be aligned to the hour, got {dt.isoformat()}"
        )
    return dt


def dt_floor_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


assert CONFIG["collection"]["delta_hours"] == 1, "delta_hours != 1 in config"

ALIGNED_START_DATETIME = dt_check_utc_aligned(CONFIG["collection"]["start_datetime"])
ALIGNED_END_DATETIME = (
    dt_check_utc_aligned(CONFIG["collection"]["end_datetime"])
    if CONFIG["collection"]["end_datetime"]
    else dt_floor_to_hour(datetime.now(timezone.utc))
)

assert ALIGNED_START_DATETIME < ALIGNED_END_DATETIME, (
    "start_datetime must be before end_datetime"
)

CONFIG["collection"]["aligned_start_datetime"] = ALIGNED_START_DATETIME
CONFIG["collection"]["aligned_end_datetime"] = ALIGNED_END_DATETIME

assert 0 < CONFIG["staging"]["coord_tolerance"] < 1, (
    "coord_tolerance should be a small degree value, not km/m"
)
assert 0 <= CONFIG["staging"]["coord_decimal_precision"] <= 8
