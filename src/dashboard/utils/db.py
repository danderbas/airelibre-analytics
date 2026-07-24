import duckdb

from src.config import CONFIG


def db_connection(DB_PATH=CONFIG["paths"]["db_path"]):
    return duckdb.connect(DB_PATH)
