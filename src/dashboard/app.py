import datetime

import streamlit as st

st.set_page_config(page_title="airelibre analytics", layout="wide")

from src.dashboard.components import aqi_heatmap, aqi_plot, geo_map
from src.dashboard.config import (
    init_config,
    options,
    update_config,
    update_date_range_input,
    update_date_range_slider,
)
from src.dashboard.utils import sidebar_title

init_config()

with st.sidebar:
    st.html(sidebar_title)

    widget_key = "w_date_range_slider"
    if widget_key not in st.session_state:
        st.session_state["w_date_range_slider"] = (
            st.session_state.config["date_range"]["start"],
            st.session_state.config["date_range"]["end"],
        )
    st.slider(
        "date slider",
        min_value=datetime.date(2022, 1, 1),  # might get min date from data
        max_value=datetime.date.today(),
        key=widget_key,
        on_change=update_date_range_slider,
        format="DD/MM/YYYY",
        label_visibility="hidden",
    )

    widget_key = "w_date_range_start"
    widget_label = "from"
    config_keys = ("date_range", "start")
    # reqired to fix initial value not being set (conflict between key and value)
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.config["date_range"]["start"]
    st.date_input(
        widget_label,
        key=widget_key,
        on_change=update_date_range_input,
    )

    widget_key = "w_date_range_end"
    widget_label = "to"
    config_keys = ("date_range", "end")
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.config["date_range"]["end"]
    st.date_input(
        widget_label,
        key=widget_key,
        on_change=update_date_range_input,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    widget_key = "w_map_toggle"
    widget_label = "show map"
    config_keys = ("map", "show")
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.config["map"]["show"]
    st.toggle(
        widget_label,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    widget_key = "w_plot_temporal_granularity"
    widget_label = "(plot) rolling average window"
    config_keys = ("plot", "granularity", "temporal")
    w_options = options["plot"]["granularity"]["temporal"]
    st.selectbox(
        widget_label,
        options=w_options,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    widget_key = "w_plot_spatial_granularity"
    widget_label = "(plot) spatial granularity"
    config_keys = ("plot", "granularity", "spatial")
    w_options = options["plot"]["granularity"]["spatial"]
    st.selectbox(
        widget_label,
        options=w_options,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    widget_key = "w_heatmap_temporal_granularity"
    widget_label = "(heatmap) temporal granularity"
    config_keys = ("heatmap", "granularity", "temporal")
    w_options = options["heatmap"]["granularity"]["temporal"]
    st.selectbox(
        widget_label,
        options=w_options,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    widget_key = "w_heatmap_spatial_granularity"
    widget_label = "(heatmap) spatial granularity"
    config_keys = ("heatmap", "granularity", "spatial")
    w_options = options["heatmap"]["granularity"]["spatial"]
    st.selectbox(
        widget_label,
        options=w_options,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    widget_key = "w_heatmap_value"
    widget_label = "heatmap value"
    config_keys = ("heatmap", "value")
    w_options = options["heatmap"]["value"]
    st.selectbox(
        widget_label,
        options=w_options,
        key=widget_key,
        on_change=update_config,
        args=(widget_key, *config_keys),
    )

    # option: (heatmap) show aqi colormap or vales


if st.session_state.config["map"]["show"]:
    col_map, col_plot = st.columns([3, 7])
    with col_map:
        st.plotly_chart(geo_map(), height="stretch", width="content")
    with col_plot:
        st.plotly_chart(aqi_plot(), height="stretch", width="stretch")
else:
    st.plotly_chart(aqi_plot(), height="stretch", width="stretch")

st.markdown("<br>", unsafe_allow_html=True)

st.plotly_chart(aqi_heatmap(), height="stretch", width="stretch")
