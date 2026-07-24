#!/usr/bin/env python3
"""
collects sensor data from airelib.re's API (air quality sensor data)

GET request params: start, end (datetime, ISO datetime format)
(see https://api.airelib.re/docs)

requested intervals:
[start(n), end(n)]
= [START_DATE + n*DELTA_HOURS, START_DATE + (n+1)*DELTA_HOURS)
(for n = 0 until end(n) < now)

- script is idempotent, skipping data already saved
- successful responses saved in jsonl files
    (JSON lines, each line being a json object
    and one file per day under RAW_DIR/
      e.g. RAW_DIR/2024-01-01.jsonl)
- retries up to MAX_RETRIES (with exponential backoff)
"""

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from src.config import CONFIG, END_DATETIME, START_DATETIME

log = logging.getLogger(__name__)

RAW_DIR = Path(CONFIG["paths"]["raw_dir"])


def main():
    log.info(
        "fetching api data (%s -> %s)",
        iso_format(START_DATETIME),
        iso_format(END_DATETIME),
    )

    DELTA_HOURS = CONFIG["ingestion"]["delta_hours"]

    intervals = list(generate_intervals(START_DATETIME, END_DATETIME, DELTA_HOURS))
    completed = load_completed_from_raw()  # to avoid reprocessing
    log.info(
        "%d api calls pending (completed = %d/%d, %0.1f %%)",
        len(intervals) - len(completed),
        len(completed),
        len(intervals),
        100 * len(completed) / float(len(intervals)),
    )

    success_count = 0
    fail_count = 0
    skip_count = 0

    for start_datetime, end_datetime in intervals:
        key = iso_format(start_datetime)
        if key in completed:
            skip_count += 1
            continue

        data = fetch_api_data(start_datetime, end_datetime)

        if data is not None:
            save_response(start_datetime, end_datetime, data)
            success_count += 1
        else:
            fail_count += 1

    log.info("added: %d (skipped: %d)", success_count, skip_count)

    if fail_count:
        log.warning("pending (failed): %d", fail_count)
        log.info("rerun to fetch pending intervals' data")


def load_completed_from_raw() -> set[str]:
    """loads start times already fetched, from saved jsonl files"""
    completed = set()

    for f in RAW_DIR.glob("*.jsonl"):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    completed.add(json.loads(line)["start"])

    return completed


def iso_format(dt: datetime) -> str:
    """js Date.toISOString() format"""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def generate_intervals(start: datetime, end: datetime, delta_hours: float):
    delta = timedelta(hours=delta_hours)
    cursor = start
    while cursor + delta <= end:
        nxt = cursor + delta
        yield cursor, nxt
        cursor = nxt


def fetch_api_data(start: datetime, end: datetime) -> list[dict] | None:
    """
    GET request (parameters: start, end), retry with exponential backoff
    returns parsed JSON (success) | None (if all retries failed)
    """
    requests_config = CONFIG["ingestion"]["requests"]

    API_URL = requests_config["api_url"]
    MAX_RETRIES = requests_config["max_retries"]
    REQUEST_BACKOFF_BASE = requests_config["backoff_base_seconds"]
    REQUEST_TIMEOUT = requests_config["timeout_seconds"]

    params = {
        "start": iso_format(start),
        "end": iso_format(end),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            log.warning(
                "failed %d/%d for %s - %s (%s)",
                attempt,
                MAX_RETRIES,
                params["start"],
                params["end"],
                e,
            )
            if attempt < MAX_RETRIES:
                sleep_for = REQUEST_BACKOFF_BASE * (2 ** (attempt - 1))
                time.sleep(sleep_for)

    log.error(
        "%d attempts failed for interval [%s, %s)",
        MAX_RETRIES,
        params["start"],
        params["end"],
    )
    return None


def save_response(start: datetime, end: datetime, data: list):
    """
    save responses to jsonl file

    files partitioned by 'start' day
      (e.g. start='2024-01-01T23:00:00Z' records
      appended to RAW_DIR/2024-01-01.jsonl)
    """
    day_str = start.strftime("%Y-%m-%d")
    out_path = RAW_DIR / f"{day_str}.jsonl"

    record = {
        "start": iso_format(start),
        "end": iso_format(end),
        "data": data,
    }

    with open(out_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    log.info("+[%s, %s) -> %s", iso_format(start), iso_format(end), out_path)


if __name__ == "__main__":
    main()
