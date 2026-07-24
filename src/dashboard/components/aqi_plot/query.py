import pandas as pd
import streamlit as st

from src.dashboard.utils.db import db_connection


# @st.cache_data
def fetch() -> pd.DataFrame:
    config = st.session_state.config

    date_start = config["date_range"]["start"]
    date_end = config["date_range"]["end"]

    with db_connection() as con:
        return con.query(f"""
            SELECT *
            FROM main.mart_aqi
            WHERE dt::DATE >= '{date_start.strftime("%Y-%m-%d")}'
                AND dt::DATE <= '{date_end.strftime("%Y-%m-%d")}'
            ORDER BY id, dt
        """).df()
