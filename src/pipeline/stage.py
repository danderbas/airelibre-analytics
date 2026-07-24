import logging

import duckdb

from src.config import CONFIG

log = logging.getLogger(__name__)


def main():
    DB_PATH = CONFIG["paths"]["db_path"]
    COORD_PRECISION = CONFIG["staging"]["coord_decimal_precision"]

    log.info("staging raw data...")

    with duckdb.connect(DB_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS staging;")

        log.info("writing staging.readings table...")
        con.execute(f"""
            CREATE OR REPLACE TABLE staging.readings AS
            -- unnest arrays
            WITH exploded_raw AS (
                SELECT
                    start,
                    "end",
                    UNNEST(data) AS item
                FROM raw.readings
            ),
            -- flatten items and round coordinate values 
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
                FROM exploded_raw
            ),
            -- flag to later filter
            flagged_data AS (
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
                FROM flattened_data
            ),
            -- filter out bad data
            renamed_and_keyed AS (
                SELECT
                    *
                    EXCLUDE (quality_category, is_valid_payload, is_in_paraguay)
                    RENAME (
                        "source" AS sensor_hash,
                        sensor AS sensor_type,
                        description AS sensor_desc,
                        start AS start_dt,
                        "end" as end_dt,
                        latitude as lat,
                        longitude as lon,
                        quality_index as aqi
                    )
                FROM flagged_data
                WHERE is_valid_payload = TRUE
                  AND is_in_paraguay = TRUE
            ),
            deduplicated AS (
                SELECT *,
                       ROW_NUMBER() OVER(
                           PARTITION BY sensor_type, sensor_hash, start_dt
                           ORDER BY end_dt DESC
                       ) AS row_num
                FROM renamed_and_keyed
            )
            SELECT * EXCLUDE (row_num)
            FROM deduplicated
            WHERE row_num = 1;
        """)

    log.info("staging completed")


if __name__ == "__main__":
    main()
