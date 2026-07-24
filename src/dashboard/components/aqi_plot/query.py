import pandas as pd
import streamlit as st

from src.dashboard.utils.db import db_connection


#@st.cache_data
def fetch() -> pd.DataFrame:
    config = st.session_state.config

    spatial_granularity = config["plot"]["granularity"]["spatial"]
    date_start = config["date_range"]["start"]
    date_end = config["date_range"]["end"]

    with db_connection() as con:
        return con.query(f"""
            SELECT *
            FROM {table(spatial_granularity)}
            WHERE dt::DATE >= '{date_start.strftime("%Y-%m-%d")}'
                AND dt::DATE <= '{date_end.strftime("%Y-%m-%d")}'
        """).df()

def table(spatial_granularity):
    match spatial_granularity:
        case "location":
            return "dev.fct_locations_aqi_rollavgs"
        case "area":
            return "dev.fct_areas_avg_aqi_rollavgs"
