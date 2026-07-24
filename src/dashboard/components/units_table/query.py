import pandas as pd
import streamlit as st


def units_table_df() -> (pd.DataFrame, list):
    df: pd.DataFrame = st.session_state["units"].copy()
    spatial_grain = st.session_state.config["granularity"]["spatial"].lower()

    # filter by chosen spatial grain and show only those in current date range
    df = df[(df["spatial_grain"] == spatial_grain) & (df["in_selected_date_range"])]

    st.session_state["units_index"] = df.index.to_list()

    df["lifespan_months"] = df["lifespan_months"].round(1)

    df = df[
        [
            "show",
            "description",
            "area_label",
            "id",
            "first_dt",
            "last_dt",
            "lifespan_months",
            "coverage_pct",
            "latitude",
            "longitude",
            "device_id",
            "device_type",
        ]
    ]

    df.rename(
        columns={
            "show": "",
            "description": "Description",
            "area_label": "Area",
            "first_dt": "From",
            "last_dt": "To",
            "lifespan_months": "Age (months)",
            "coverage_pct": "Coverage",
            "latitude": "lat",
            "longitude": "lon",
            "device_type": "Device",
        },
        inplace=True,
    )

    if spatial_grain == "location":
        cols = [
            "",
            "Description",
            "Area",
            "Coverage",
            "From",
            "To",
            "Age (months)",
            "lat",
            "lon",
            "Device",
        ]
        return df[cols], cols[1:]  # columns to disable
    else:
        cols = ["", "Area", "From", "To", "Age (months)"]
        return df[cols], cols[1:]
