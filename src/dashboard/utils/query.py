import pandas as pd
import streamlit as st

from src.dashboard.utils.db import db_connection


@st.cache_data
def fetch_aqi_scale() -> pd.DataFrame:
    with db_connection() as con:
        return con.query("""
        SELECT
            *,
            0.5*(min_aqi + max_aqi)
                AS mid_aqi,
            min_aqi::text || ' - ' || max_aqi::text
                AS aqi_range
        FROM main.aqi_scale
        """).df()


@st.cache_data
def fetch_units() -> pd.DataFrame:
    with db_connection() as con:
        return con.query("""
        SELECT *
        FROM main.mart_units
        ORDER BY spatial_grain, area_label, description
        """).df()


def fetch_time_bounds():
    df = fetch_units()

    return df["first_dt"].min().date(), df["last_dt"].max().date()
