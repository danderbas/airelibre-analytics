import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _load_config() -> dict:
    config_path = os.environ.get(
        "CONFIG_PATH", str(Path(__file__).parent.parent / "config.yaml")
    )

    with open(config_path) as f:
        config = yaml.safe_load(f)

    def initialize_directories():
        Path(config["paths"]["raw_dir"]).mkdir(parents=True, exist_ok=True)
        Path(config["paths"]["db_path"]).parent.mkdir(parents=True, exist_ok=True)

    def align_datetimes_to_hour():
        def dt_floor_to_hour(val: str | datetime) -> datetime:
            dt = datetime.fromisoformat(val) if isinstance(val, str) else val
            return dt.replace(minute=0, second=0, microsecond=0)

        raw_start = config["ingestion"]["start_datetime"]
        raw_end = config["ingestion"].get("end_datetime") or datetime.now(timezone.utc)

        return (dt_floor_to_hour(raw_start), dt_floor_to_hour(raw_end))

    def verify_assertions():
        def dt_is_utc_z(dt: datetime) -> bool:
            return dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0

        assert dt_is_utc_z(START_DATETIME) and dt_is_utc_z(START_DATETIME), (
            "datetimes should be utc with zero offset (iso strings ending with Z)"
        )

        assert START_DATETIME < END_DATETIME, (
            "start_datetime must come before end_datetime"
        )

        assert config["ingestion"]["delta_hours"] == 1, "delta_hours != 1 in config"

        requests = config["ingestion"]["requests"]
        assert requests["api_url"].startswith("http"), "api_url must be a full URL"
        assert requests["max_retries"] > 0
        assert requests["timeout_seconds"] > 0

        assert 0 <= config["staging"]["coord_decimal_precision"] <= 8

    initialize_directories()

    START_DATETIME, END_DATETIME = align_datetimes_to_hour()

    verify_assertions()

    return config, START_DATETIME, END_DATETIME


CONFIG, START_DATETIME, END_DATETIME = _load_config()
