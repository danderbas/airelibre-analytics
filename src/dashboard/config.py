import datetime
import operator
from functools import reduce

import pandas as pd
import streamlit as st

from src.dashboard.utils import SIDEBAR_TITLE
from src.dashboard.utils.query import fetch_time_bounds, fetch_units

options = {
    "granularity": {"spatial": ["Location", "Area"]},
    "plot": {
        "granularity": {
            "temporal": ["Hour", "Day", "Week", "Month"],  # window
        }
    },
    "heatmap": {
        "value": [
            "p90_aqi",
            "median_aqi",
            "avg_aqi",
            "std_aqi",
            "max_aqi",
            "min_aqi",
        ],
        "granularity": {
            "temporal": ["Day", "Week", "Month"],
        },
    },
}

default_config = {
    "granularity": {"spatial": "Location"},
    "date_range": {
        "start": datetime.date(2025, 1, 1),
        "end": datetime.date(2026, 1, 1),
    },
    "map": {"show": True, "show_locations": True, "show_areas": True},
    "table": {"show": True},
    "plot": {
        "show": True,
        "granularity": {
            "temporal": "Day",
        },
        "show_values": True,
        "show_avg": False,
    },
    "heatmap": {
        "show": True,
        "value": "p90_aqi",
        "aqi_scale": True,
        "granularity": {
            "temporal": "Day",
        },
    },
}


def init_config():
    if "config" not in st.session_state:
        st.session_state["config"] = default_config


def init_units():
    if "units" not in st.session_state:
        df: pd.DataFrame = fetch_units()

        df["show"] = False

        st.session_state["units"] = df
        update_units_in_selected_date_range()
        show_some_units()


def show_some_units():
    df = st.session_state["units"]

    target_indices = df[
        (df["spatial_grain"] == "location") & (df["in_selected_date_range"])
    ].index[0:6]
    df.loc[target_indices, "show"] = True


def update_units_in_selected_date_range():
    date_range_start = st.session_state.config["date_range"]["start"]
    date_range_end = st.session_state.config["date_range"]["end"]

    df = st.session_state["units"]

    df["in_selected_date_range"] = (date_range_start < df["last_dt"].dt.date) & (
        df["first_dt"].dt.date < date_range_end
    )


def update_config(widget_key, *config_keys):
    """drill down config with keys config_keys,
    save widget's new value into config[*config_keys]"""
    reduce(operator.getitem, config_keys[:-1], st.session_state.config)[
        config_keys[-1]
    ] = st.session_state[widget_key]


def update_date_range_slider():
    date_start, date_end = st.session_state["w_date_range_slider"]

    st.session_state.config["date_range"]["start"] = date_start
    st.session_state.config["date_range"]["end"] = date_end

    st.session_state["w_date_range_start"] = date_start
    st.session_state["w_date_range_end"] = date_end

    update_units_in_selected_date_range()


def update_date_range_input():
    date_start = st.session_state["w_date_range_start"]
    date_end = st.session_state["w_date_range_end"]

    st.session_state.config["date_range"]["start"] = date_start
    st.session_state.config["date_range"]["end"] = date_end

    st.session_state["w_date_range_slider"] = (date_start, date_end)

    update_units_in_selected_date_range()


def init_sidebar():
    min_date, max_date = fetch_time_bounds()

    with st.sidebar:
        st.html(SIDEBAR_TITLE)

        st.markdown("<br><br>", unsafe_allow_html=True)

        widget_key = "w_date_range_slider"
        if widget_key not in st.session_state:
            st.session_state["w_date_range_slider"] = (
                st.session_state.config["date_range"]["start"],
                st.session_state.config["date_range"]["end"],
            )
        st.slider(
            "date slider",
            min_value=min_date,
            max_value=max_date,
            key=widget_key,
            on_change=update_date_range_slider,
            format="DD/MM/YYYY",
            label_visibility="hidden",
        )

        col_from, col_to = st.columns([1, 1])
        with col_from:
            widget_key = "w_date_range_start"
            widget_label = "from"
            # reqired to set initial value (avoids conflict between widgetkey and value)
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["date_range"][
                    "start"
                ]
            st.date_input(
                widget_label,
                key=widget_key,
                on_change=update_date_range_input,
                min_value=min_date,
                max_value=max_date,
            )
        with col_to:
            widget_key = "w_date_range_end"
            widget_label = "to"
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["date_range"][
                    "end"
                ]
            st.date_input(
                widget_label,
                key=widget_key,
                on_change=update_date_range_input,
                min_value=min_date,
                max_value=max_date,
            )

        st.markdown("<br><br>", unsafe_allow_html=True)

        col_units, col_aqi = st.columns([1, 1])

        with col_units:
            widget_key = "w_map_toggle"
            widget_label = "Map"
            config_keys = ("map", "show")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["map"]["show"]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

            widget_key = "w_table_toggle"
            widget_label = "Table"
            config_keys = ("table", "show")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["table"]["show"]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

        with col_aqi:
            widget_key = "w_plot_toggle"
            widget_label = "Plot"
            config_keys = ("plot", "show")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["plot"]["show"]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

            widget_key = "w_heatmap_toggle"
            widget_label = "Heatmap"
            config_keys = ("heatmap", "show")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["heatmap"][
                    "show"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )


def update_units_config():
    edited_rows = st.session_state["w_units_table"]["edited_rows"]
    units_index = st.session_state["units_index"]

    show_values = {units_index[k]: bool(v[""]) for k, v in edited_rows.items()}

    for k, v in show_values.items():
        st.session_state.units.loc[k, "show"] = v
