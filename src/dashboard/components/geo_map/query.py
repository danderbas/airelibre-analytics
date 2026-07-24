import pandas as pd
import streamlit as st

from src.dashboard.utils.db import db_connection


@st.cache_data
def fetch_areas() -> pd.DataFrame:
    with db_connection() as con:
        return con.query("""
        SELECT *
        FROM main.int_areas
        WHERE max_distance_from_asucentro_km IS NOT NULL
        """).df()
