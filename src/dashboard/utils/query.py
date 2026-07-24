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
                as mid_aqi,
            min_aqi::text || ' - ' || max_aqi::text
                as aqi_range
        FROM dev.aqi_scale
        """).df()
