import datetime
import operator
from functools import reduce

import streamlit as st

options = {
    "plot": {
        #"ravg_window": ["day", "week", "month"],
        "granularity": {
            "temporal": ["hour", "day", "week", "month"], # this will define the window
            "spatial": ["location", "area"],
        },
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
            "temporal": ["day", "week", "month"],
            "spatial": ["location", "area"],
        },
    },
}

default_config = {
    "date_range": {
        "start": datetime.date(2025, 1, 1),
        "end": datetime.date(2026, 1, 1),
    },
    "map": {"show": True},
    "plot": {
        "granularity": {
            "temporal": "day",
            "spatial": "location",
        },
    },
    "heatmap": {
        "value": "p90_aqi",
        "granularity": {
            "temporal": "day",
            "spatial": "location",
        },
    },
}

def init_config():
    if "config" not in st.session_state:
        st.session_state["config"] = default_config

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

def update_date_range_input():
    date_start = st.session_state["w_date_range_start"]
    date_end = st.session_state["w_date_range_end"]

    st.session_state.config["date_range"]["start"] = date_start
    st.session_state.config["date_range"]["end"] = date_end

    st.session_state["w_date_range_slider"] = (date_start, date_end)
