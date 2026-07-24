import pandas as pd
import streamlit as st

from src.dashboard.utils.db import db_connection


def fetch() -> pd.DataFrame:
    config = st.session_state.config

    temporal_granularity = config["heatmap"]["granularity"]["temporal"].lower()
    date_start = config["date_range"]["start"]
    date_end = config["date_range"]["end"]

    with db_connection() as con:
        return con.query(f"""
        SELECT
            *,
            STRFTIME(period_start, '%Y-%m-%d')
                AS date_key
        FROM main.mart_aqi_periods_stats
        WHERE time_grain = '{temporal_granularity}'
            AND period_start >= '{date_start.strftime("%Y-%m-%d")}'
            AND period_end <= '{date_end.strftime("%Y-%m-%d")}'
        ORDER BY period_start
        """).df()
