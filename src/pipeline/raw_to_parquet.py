#!/usr/bin/env python3
"""
consolidates raw data (in data/raw/*.jsonl) into a single parquet file
"""

import json
import logging
from pathlib import Path

import polars as pl

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/consolidated.parquet")


def extract_records(window_start: str, window_end: str, data: list) -> list[dict]:
    for item in data:
        item["start"] = window_start
        item["end"] = window_end
    return data


def main():
    files = sorted(RAW_DIR.glob("*.jsonl"))
    if not files:
        log.warning("No JSONL files found in %s", RAW_DIR)
        return

    log.info("Loading %d day-files...", len(files))
    records = []
    for f in files:
        with open(f) as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # print(entry)
                    er = extract_records(entry["start"], entry["end"], entry["data"])

                    records.extend(
                        er  # extract_records(entry["start"], entry["end"], entry["data"])
                    )

                except (json.JSONDecodeError, KeyError) as e:
                    log.error("Failed to parse %s line %d: %s", f, line_no, e)

    if not records:
        log.warning("No records extracted, nothing to write.")
        return

    # print(records)

    df = (
        pl.DataFrame(records, infer_schema_length=None)
        .with_columns(
            [
                pl.col("start").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
                pl.col("end").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
                pl.col("quality").struct.field("category").alias("quality_category"),
                pl.col("quality").struct.field("index").alias("quality_index"),
            ]
        )
        .drop("quality")
    )
    df.write_parquet(OUT_FILE)
    log.info("Wrote %d rows to %s", len(df), OUT_FILE)
    print(df.head())


if __name__ == "__main__":
    main()
