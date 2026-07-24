"""
builds core data layer, from staging layer data

takes into account that a sensor might change location
therefore a surrogate 'located_sensor_id' is generated
each time a location change is detected

(note: while the 'source' field identifies most sensors uniquely,
       in a few cases this value appears duplicated
       (see 41ce3d, 8eb9)
       so we also define a surrogate 'device_id')

input table:
    - 'staging.readings'
output tables:
    - 'core.located_sensors'
    - 'core.readings'

(overwrites tables each time, re-run safe)
"""

import hashlib
import logging

import duckdb
import polars as pl

from src.config import CONFIG
from src.pipeline import log_df_stats

log = logging.getLogger(__name__)

DB_PATH = CONFIG["paths"]["db_path"]
COORD_TOLERANCE = CONFIG["core"]["coord_tolerance"]


def main():
    log.info("loading records from staging.readings...")

    with duckdb.connect(DB_PATH) as con:
        stg_df = con.execute("""
            SELECT
                SUBSTRING(SHA1(sensor_hash || sensor_type), 1, 8)
                    AS device_id,
                sensor_type,
                sensor_hash,
                sensor_desc,
                start_dt,
                end_dt,
                lat,
                lon,
                aqi
            FROM staging.readings
            ORDER BY sensor_type, sensor_hash, start_dt;
        """).pl()

    if stg_df.is_empty():
        log.warning("no staging data found!")
        return

    events = stg_df.to_dicts()

    # detect location changes and assign located_sensor_ids
    events_with_lsid, located_sensor_rows = assign_located_sensors(events)
    log.info(
        "detected %d locations",
        len(located_sensor_rows),
    )

    # create core (sensors) dimension df
    sensors_df = pl.DataFrame(located_sensor_rows).with_columns(
        [
            pl.col("first_start_dt").cast(pl.Datetime),
            pl.col("last_end_dt").cast(pl.Datetime, strict=False),
        ]
    )

    # core readings fact df per located_sensor
    readings_df = (
        pl.DataFrame(events_with_lsid, infer_schema_length=None)
        .with_columns(
            [
                pl.col("start_dt").cast(pl.Datetime),
                pl.col("end_dt").cast(pl.Datetime),
            ]
        )
        .rename({"located_sensor_id": "lsid", "start_dt": "dt"})
        .drop(
            [
                "lat",
                "lon",
                "sensor_hash",
                "sensor_type",
                "sensor_desc",
                "end_dt",
                "device_id",
            ]
        )
    )

    validate(sensors_df, readings_df)

    with duckdb.connect(DB_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS core;")

        con.execute("""
        CREATE OR REPLACE TABLE core.dim_sensors AS
        SELECT * FROM sensors_df;
        """)

        con.execute("""
        CREATE OR REPLACE TABLE core.fct_readings AS
        SELECT * FROM readings_df;
        """)

    log_df_stats(__name__, sensors_df, "core.dim_sensors")
    log_df_stats(__name__, readings_df, "core.fct_readings")
    log.info("populated core layers table: core.dim_sensors and core.fct_readings")


def coords_match(
    lat1: float, lon1: float, lat2: float, lon2: float, tol=COORD_TOLERANCE
) -> bool:
    return abs(lat1 - lat2) <= tol and abs(lon1 - lon2) <= tol


def generate_located_sensor_surrogate_key(
    device_id: str, lat: float, lon: float, first_start_dt: str
) -> str:
    raw = f"{device_id}|{lat}|{lon}{first_start_dt}"
    return hashlib.sha1(raw.encode()).hexdigest()[:8]


def assign_located_sensors(events: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    walk pre-sorted events (by device_id, start_dt),
    assigns located_sensor_id to each event

    when coordinate change is detected, generates a new located_sensor

    returns events_with_lsid, located_sensor
    """
    located_sensors = []
    current_active_sensors = {}  # maps device_id -> active tracking dict
    previous_event = None

    for e in events:
        device_id = e["device_id"]
        lat, lon = e["lat"], e["lon"]
        current = current_active_sensors.get(device_id)

        # if a new sensor appears or if coordinates shifted past tolerance
        if current is None or not coords_match(
            current["lat"], current["lon"], lat, lon
        ):
            if current is not None:
                current["last_end_dt"] = previous_event["end_dt"]

            lsid = generate_located_sensor_surrogate_key(
                device_id, lat, lon, str(e["start_dt"])
            )
            new_located_sensor = {
                "located_sensor_id": lsid,
                "device_id": device_id,
                "sensor_hash": e["sensor_hash"],
                "sensor_type": e["sensor_type"],
                "sensor_desc": e["sensor_desc"],
                "lat": lat,
                "lon": lon,
                "first_start_dt": e["start_dt"],
                "last_end_dt": None,
            }
            located_sensors.append(new_located_sensor)
            current_active_sensors[device_id] = new_located_sensor
            current = new_located_sensor  # not really needed because events are sorted
        else:
            # use last description always (in case it is updated)
            current["sensor_desc"] = e["sensor_desc"]

        e["located_sensor_id"] = current["located_sensor_id"]
        previous_event = e

    return events, located_sensors


def validate(sensors_df: pl.DataFrame, readings_df: pl.DataFrame):
    assert sensors_df["located_sensor_id"].n_unique() == len(sensors_df), (
        "duplicate located_sensor_id found in core dim table"
    )

    invalid_times = sensors_df.filter(
        pl.col("last_end_dt").is_not_null()
        & (pl.col("first_start_dt") >= pl.col("last_end_dt"))
    )
    assert len(invalid_times) == 0, (
        f"chronological Error: last_end_dt <= first_start_dt:\n{invalid_times}"
    )

    orphaned = readings_df.join(
        sensors_df, left_on="lsid", right_on="located_sensor_id", how="anti"
    )
    assert len(orphaned) == 0, (
        f"relational integrity error: orphaned readings found\n{orphaned}"
    )

    duplicates = readings_df.group_by(["lsid", "dt"]).len().filter(pl.col("len") > 1)
    assert len(duplicates) == 0, (
        f"uniqueness Error: duplicate records found for time-series\n{duplicates}"
    )

    for col in ["lsid", "dt", "aqi"]:
        null_count = readings_df[col].null_count()
        assert null_count == 0, f"null '{col}' contains {null_count} nulls"


if __name__ == "__main__":
    main()
