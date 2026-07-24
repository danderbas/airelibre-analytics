import logging
from pathlib import Path

import duckdb

from src.config import CONFIG

log = logging.getLogger(__name__)


def main():
    raw_path = Path(CONFIG["paths"]["raw_dir"])
    DB_PATH = CONFIG["paths"]["db_path"]

    jsonl_pattern = str(raw_path / "*.jsonl")

    if not any(raw_path.glob("*.jsonl")):
        log.warning("no jsonl files found in %s", str(raw_path))
        return

    log.info("dumping raw data...")

    with duckdb.connect(DB_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        log.info("writing raw.readings table...")

        con.execute(f"""
            CREATE OR REPLACE TABLE raw.readings AS
            SELECT *
            FROM read_ndjson('{jsonl_pattern}')
        """)

    log.info("raw dump completed")


if __name__ == "__main__":
    main()
