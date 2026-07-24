import logging
from pathlib import Path

import duckdb

from src.config import CONFIG

log = logging.getLogger(__name__)


def main():
    raw_path = Path(CONFIG["paths"]["raw_dir"])
    COORD_PRECISION = CONFIG["staging"]["coord_decimal_precision"]
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
            WITH exploded_json AS (
                SELECT
                    start,
                    "end",
                    unnest(data) AS item
                FROM read_ndjson('{jsonl_pattern}')
            ),
            flattened_data AS (
                SELECT
                    start,
                    "end",
                    item.source AS "source",
                    item.sensor AS sensor,
                    TRIM(BOTH '"' FROM item.description::VARCHAR) AS description,
                    ROUND(CAST(item.latitude AS DOUBLE), {COORD_PRECISION})
                        AS latitude,
                    ROUND(CAST(item.longitude AS DOUBLE), {COORD_PRECISION})
                        AS longitude,
                    item.quality.category AS quality_category,
                    CAST(item.quality.index AS INTEGER) AS quality_index
                FROM exploded_json
            )
            SELECT
                *,
                (
                    sensor IS NOT NULL AND
                    "source" IS NOT NULL AND
                    description IS NOT NULL AND
                    latitude BETWEEN -90 AND 90 AND
                    longitude BETWEEN -180 AND 180 AND
                    quality_index IS NOT NULL AND
                    quality_index BETWEEN 0 AND 500
                ) AS is_valid_payload,
                (
                    latitude BETWEEN -27.5 AND -19.0 AND
                    longitude BETWEEN -62.5 AND -54.0
                ) AS is_in_paraguay
            FROM flattened_data;
        """)

    log.info("raw dump completed")


if __name__ == "__main__":
    main()
