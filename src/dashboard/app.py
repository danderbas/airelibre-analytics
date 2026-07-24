import streamlit as st

from src.dashboard.components import aqi_heatmap, aqi_plot, geo_map
from src.dashboard.components.units_table.query import units_table_df
from src.dashboard.config import (
    init_config,
    init_sidebar,
    init_units,
    options,
    update_config,
    update_units_config,
)
from src.dashboard.utils.ui import toggle_show

st.set_page_config(page_title="airelibre analytics", layout="wide")

init_config()
init_sidebar()
init_units()


def main():
    show_units = (
        st.session_state.config["map"]["show"]
        or st.session_state.config["table"]["show"]
    )
    show_aqi = (
        st.session_state.config["plot"]["show"]
        or st.session_state.config["heatmap"]["show"]
    )

    if show_units and show_aqi:
        col_units, col_aqi = st.columns(
            [4, 7], gap="medium", width="stretch", vertical_alignment="center"
        )
        with col_units:
            units_column()

        with col_aqi:
            aqi_column()
    elif show_units:
        units_column()
    elif show_aqi:
        aqi_column()


def units_column():
    if st.session_state.config["map"]["show"]:
        # (only show with colors the sensors in current range)
        st.plotly_chart(
            geo_map(),
            width="content",
        )

        col_map_l, col_map_a = st.columns(2)
        with col_map_l:
            widget_key = "w_map_locations_show"
            widget_label = "Locations"
            config_keys = ("map", "show_locations")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["map"][
                    "show_locations"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )
        with col_map_a:
            widget_key = "w_map_areas_show"
            widget_label = "Areas"
            config_keys = ("map", "show_areas")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["map"][
                    "show_areas"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

    if st.session_state.config["table"]["show"]:
        col_table_s, col_table_b = st.columns(2, vertical_alignment="bottom")
        with col_table_s:
            widget_key = "w_spatial_granularity"
            widget_label = "spatial granularity"
            config_keys = ("granularity", "spatial")
            w_options = options["granularity"]["spatial"]
            st.selectbox(
                widget_label,
                options=w_options,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
                label_visibility="collapsed",
            )

        with col_table_b:
            st.button("Toggle select all", on_click=toggle_show)

        lt_df, disabled_cols = units_table_df()
        st.data_editor(
            lt_df,
            key="w_units_table",
            hide_index=True,
            width="stretch",
            on_change=update_units_config,
            disabled=disabled_cols,
            column_config={
                "Coverage": st.column_config.ProgressColumn(
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
        )


def aqi_column():
    if st.session_state.config["plot"]["show"]:
        col_plot_time, col_plot_vals, col_plot_avg = st.columns(
            3, vertical_alignment="bottom"
        )

        with col_plot_time:
            widget_key = "w_plot_temporal_granularity"
            widget_label = "t"
            config_keys = ("plot", "granularity", "temporal")
            w_options = options["plot"]["granularity"]["temporal"]
            st.selectbox(
                widget_label,
                options=w_options,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
                label_visibility="collapsed",
                help="Window",
            )
        with col_plot_vals:
            widget_key = "w_aqi_plot_values_toggle"
            widget_label = "Show values"
            config_keys = ("plot", "show_values")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["plot"][
                    "show_values"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )
        with col_plot_avg:
            widget_key = "w_aqi_plot_avg_toggle"
            widget_label = "Show average"
            config_keys = ("plot", "show_avg")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["plot"][
                    "show_avg"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

        st.plotly_chart(
            aqi_plot(),
            width="stretch",
        )

        st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.config["heatmap"]["show"]:
        col_heatmap_time, col_heatmap_value, col_heatmap_scale = st.columns(
            3, vertical_alignment="bottom"
        )

        with col_heatmap_time:
            widget_key = "w_heatmap_temporal_granularity"
            widget_label = "t"
            config_keys = ("heatmap", "granularity", "temporal")
            w_options = options["heatmap"]["granularity"]["temporal"]
            st.selectbox(
                widget_label,
                options=w_options,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
                label_visibility="collapsed",
            )

        with col_heatmap_value:
            widget_key = "w_heatmap_value"
            widget_label = "Value"
            config_keys = ("heatmap", "value")
            w_options = options["heatmap"]["value"]
            st.selectbox(
                widget_label,
                options=w_options,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
                label_visibility="collapsed",
            )

        with col_heatmap_scale:
            widget_key = "w_aqi_heatmap_scale_toggle"
            widget_label = "AQI scale"
            config_keys = ("heatmap", "aqi_scale")
            if widget_key not in st.session_state:
                st.session_state[widget_key] = st.session_state.config["heatmap"][
                    "aqi_scale"
                ]
            st.toggle(
                widget_label,
                key=widget_key,
                on_change=update_config,
                args=(widget_key, *config_keys),
            )

        st.plotly_chart(
            aqi_heatmap(),
            width="stretch",
        )


main()
