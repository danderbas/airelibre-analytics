import pandas as pd

from src.dashboard.utils.db import db_connection

#@st.cache_data
def fetch() -> pd.DataFrame:
    with db_connection() as con:
        return con.query("""
            SELECT *
            FROM dim_locations
        """).df()
