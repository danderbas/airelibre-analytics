import logging

import polars as pl


def log_df_stats(log_name: str, df: pl.DataFrame, name: str):
    log = logging.getLogger(log_name)

    rows, cols = df.shape
    size_mb = df.estimated_size("mb")

    log.info(f"Saved {name}: {rows} rows, {cols} cols, ~{size_mb:.2f} MB")
