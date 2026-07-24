#!/usr/bin/env python3
"""
builds staging data layer, from raw data

takes into account that a sensor might change location
therefore a surrogate 'located_sensor_id' is generated
each time a location change is detected

input:
    - raw data (jsonl files, date-partitioned, located at INPUT_DIR/%Y-%m-%d.jsonl)

output:
    - duckdb database
        - stg_located_sensors
        - stg_readings

(overwrites database tables each time, re-run safe)

"""

import hashlib
import json
import logging
from pathlib import Path

import duckdb
import polars as pl

INPUT_DIR = Path("data/raw")
DIM_LOCATED_SENSORS_FILE = Path("data/dim_located_sensors.parquet")
#OUTPUT_DIR = Path("data/readings")

DUCKDB_PATH = 

COORD_DECIMAL_DIGITS_PRECISION = 4
COORD_TOLERANCE = 0.01
# with this tolerance, ~1km of jitter is allowed in sensor location
# (we will still consider it as the same unit is coords change within that tolerance)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def main():
    log.info("loading raw events...")
    events = load_events()
    if not events:
        log.warning("no events found in %s", INPUT_DIR)
        return
    log.info("loaded %d events", len(events))

    events_with_located_sensor, located_sensor_rows = assign_located_sensors(events)

    log.info("detected %d distinct located_sensors", len(located_sensor_rows))
    for ls in located_sensor_rows:
        log.info(
            "  located_sensor_id %s | sensor_id = %s | (%.4f, %.4f) | %s -> %s",
            ls["located_sensor_id"],
            ls["sensor_id"],
            ls["latitude"],
            ls["longitude"],
            ls["first_start_dt"],
            ls["last_end_dt"] or "present",
        )

    sensors_df = pl.DataFrame(located_sensor_rows).with_columns(
        [
            pl.col("first_start_dt").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
            pl.col("last_end_dt")
            .cast(pl.String)
            .str.to_datetime("%Y-%m-%dT%H:%M:%SZ", strict=False),
        ]
    )

    valid_ids = sensors_df["located_sensor_id"].to_list()

    readings_df = (
        pl.DataFrame(events_with_located_sensor, infer_schema_length=None)
        .with_columns(
            [
                pl.col("start_dt").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
                pl.col("end_dt").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
            ]
        )
        .drop(["latitude", "longitude", "sensor_id", "sensor_desc"])
        .filter(pl.col("located_sensor_id").is_in(valid_ids))
    )

    validate(sensors_df, readings_df)

    save_to_duckdb(sensors_df, readings_df)

    log.info("done!")


def load_events() -> list[dict]:
    """
    flatten json raw data into list:
    one item (event) per (start, end, sensor, reading)
    """
    def in_paraguay(lat, lon):
        """
        check if location is inside paraguay (expected),
        to filter out weird coordinates
        """
        return -27.5 <= lat <= -19.0 and -62.5 <= lon <= -54.0

    events = []
    for f in sorted(INPUT_DIR.glob("*.jsonl")):
        with open(f) as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    log.error("bad JSON in %s line %d: %s", f, line_no, e)
                    continue

                start_dt = entry["start"]
                end_dt = entry["end"]
                items = entry["data"]

                for item in items:
                    if in_paraguay(item["latitude"], item["longitude"]):
                        events.append(
                            {
                                "start_dt": start_dt,
                                "end_dt": end_dt,
                                # take the pair as the (unique) sensor-id
                                "sensor_id": (item["source"], item["sensor"]),
                                "sensor_desc": item["description"] if not None else "",
                                "latitude": round(
                                    item["latitude"], COORD_DECIMAL_DIGITS_PRECISION
                                ),
                                "longitude": round(
                                    item["longitude"], COORD_DECIMAL_DIGITS_PRECISION
                                ),
                                "air_quality_index": item["quality"]["index"],
                            }
                        )

    # at some (very few) datetimes, sensor data appears duplicated
    # so we need to deduplicate it
    seen_keys = set()
    deduped_events = []
    events_sorted = sorted(events, key=lambda e: (e["sensor_id"], e["start_dt"]))
    for e in events_sorted:
        # a sensor can only be present at one location, at a given time
        key = (e["sensor_id"], e["start_dt"])

        if key not in seen_keys:
            seen_keys.add(key)
            deduped_events.append(e)
        else:
            log.warning("duplicate event dropped: %s", str(e))

    return deduped_events


def coords_match(lat1, lon1, lat2, lon2, tol=COORD_TOLERANCE) -> bool:
    return abs(lat1 - lat2) <= tol and abs(lon1 - lon2) <= tol


def located_sensor_id(
    sensor_id: str,
    latitude: float,
    longitude: float,
    first_start_dt: str,
) -> str:
    """
    (deterministic) surrogate key
    for (sensor_id, latitude, longitude, valid_from)
    """
    raw = f"""
        {sensor_id}
        {latitude}
        {longitude}
        {first_start_dt}
    """

    return hashlib.sha1(raw.encode()).hexdigest()[:8]


def assign_located_sensors(events: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    walk events sorted by (sensor_id, start_dt),
    assign located_sensor_id to each event

    when coordinate change is detected, generate new located_sensor

    returns events_with_located_sensor_ids, located_sensor
    """

    located_sensors = []  # rows for dim_located_sensors
    current_located_sensor = {}  # sensor_id -> current located_sensor data

    events_sorted = sorted(events, key=lambda e: (e["sensor_id"], e["start_dt"]))

    for e in events_sorted:
        sensor_id = e["sensor_id"]
        lat, lon = e["latitude"], e["longitude"]
        current = current_located_sensor.get(sensor_id)

        if current is None or not coords_match(
            current["latitude"], current["longitude"], lat, lon
        ):
            # close the previous located_sensor, if any
            if current is not None:
                current["last_end_dt"] = e["end_dt"]

            # generate a new located_sensor
            ls_id = located_sensor_id(sensor_id, lat, lon, e["start_dt"])
            new_located_sensor = {
                "located_sensor_id": ls_id,
                "sensor_id": sensor_id,
                "sensor_desc": e["sensor_desc"],
                "latitude": lat,
                "longitude": lon,
                "first_start_dt": e["start_dt"],
                "last_end_dt": None,
            }
            located_sensors.append(new_located_sensor)
            current_located_sensor[sensor_id] = new_located_sensor
        else:
            # use last description always (in case it is updated)
            current["sensor_desc"] = e["sensor_desc"]

        # assign (surrogate) located_sensor_id to event
        e["located_sensor_id"] = ls_id

    return events_sorted, located_sensors


def validate(sensors_df: pl.DataFrame, readings_df: pl.DataFrame):
    # unique located_sensor_id
    assert sensors_df["located_sensor_id"].n_unique() == len(sensors_df), (
        "duplicate located_sensor_id in dim"
    )

    # first_start_dt < last_end_dt
    invalid_times = sensors_df.filter(
        pl.col("last_end_dt").is_not_null()
        & (pl.col("first_start_dt") >= pl.col("last_end_dt"))
    )
    assert len(invalid_times) == 0, (
        f"last_end_dt <= first_start_dt in {len(invalid_times)}\
              rows:\n{invalid_times}"
    )

    # no orphaned readings
    orphaned = readings_df.filter(
        ~pl.col("located_sensor_id").is_in(sensors_df["located_sensor_id"].to_list())
    )
    assert len(orphaned) == 0, (
        f"{len(orphaned)} readings with non-existent located_sensor_id:\n\
            {orphaned['located_sensor_id'].unique()}"
    )

    # no duplicate readings
    duplicates = (
        readings_df.group_by(["located_sensor_id", "start_dt"])
        .len()
        .filter(pl.col("len") > 1)
    )
    assert len(duplicates) == 0, f"{len(duplicates)} duplicate readings:\n{duplicates}"

    # no nulls in critical columns
    for col in ["located_sensor_id", "start_dt", "air_quality_index"]:
        nulls = readings_df.filter(pl.col(col).is_null())
        assert len(nulls) == 0, f"{len(nulls)} nulls in {col}"

    # window bounds
    invalid_bounds = readings_df.filter(pl.col("start_dt") >= pl.col("end_dt"))
    assert len(invalid_bounds) == 0, (
        f"{len(invalid_bounds)} rows with start_dt >= end_dt:\n{invalid_bounds}"
    )


def save_to_duckdb(sensors_df: pl.DataFrame, readings_df: pl.DataFrame):
    con = duckdb.connect(DUCKDB_PATH)
    con.execute("""
        CREATE OR REPLACE TABLE stg_located_sensors AS
        SELECT * FROM sensors_df
    """)
    con.execute("""
        CREATE OR REPLACE TABLE stg_readings AS
        SELECT * FROM readings_df
    """)
    con.close()
    log.info("saved to %s", DUCKDB_PATH)


if __name__ == "__main__":
    main()
