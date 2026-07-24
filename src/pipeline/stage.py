import logging

import duckdb

from src.config import CONFIG

log = logging.getLogger(__name__)


def main():
    DB_PATH = CONFIG["paths"]["db_path"]

    log.info("staging raw data...")

    with duckdb.connect(DB_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS staging;")

        log.info("writing staging.readings table...")
        con.execute("""
            CREATE OR REPLACE TABLE staging.readings AS
            WITH renamed_and_keyed AS (
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
                FROM raw.readings
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
