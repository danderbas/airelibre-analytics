import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.query import fetch_aqi_scale


def render(df: pd.DataFrame) -> go.Figure:
    config = st.session_state.config

    temporal_granularity = config["heatmap"]["granularity"]["temporal"].lower()
    spatial_granularity = config["granularity"]["spatial"].lower()
    value = config["heatmap"]["value"]
    show_aqi_scale = config["heatmap"]["aqi_scale"]

    units = st.session_state.units  # units visibility and info

    df = df[
        (df["spatial_grain"] == spatial_granularity)
        & (df["id"].isin(units[units["show"]]["id"]))
    ]

    aqi_scale_df, custom_colorscale, max_overall_aqi = aqi_scale()

    period_setting, dtick_setting, format_setting = timescale_params(
        temporal_granularity
    )

    fig = go.Figure(
        data=go.Heatmap(
            x=df["date_key"],
            y=df["id"],
            z=df[value_column(value)],
            xperiod=period_setting,  #  width of each cell
            xperiodalignment="middle",
            colorscale=custom_colorscale if show_aqi_scale else "Turbo",
            zmin=0,
            zmax=max_overall_aqi,
            hoverongaps=False,
            showscale=True,  # might give option to change this
            colorbar={
                "title": "AQI",
                "tickmode": "array",
                "tickvals": aqi_scale_df["mid_aqi"],
                "ticktext": aqi_scale_df["aqi_range"],
                "thickness": 20,
            }
            if show_aqi_scale
            else None,
            # showlegend=True,
            hovertemplate=(
                f"""
                <span style='font-size: 150%;'>
                <b>%{{z:.1f}}</b> = {value} (%{{customdata[4]|%Y-%m-%d}} - %{{customdata[5]|%Y-%m-%d}})</span>
                <br><br>
                <span style='font-size: 125%;'>
                <b>%{{customdata[1]}}</b> (id %{{customdata[0]}})</span>
                <br>(%{{customdata[2]}}, %{{customdata[3]}})"""
                if spatial_granularity == "location"
                else """
                <span style='font-size: 150%;'><b>%{z:.1f}</b> = AQI(%{x})</span>
                <br><br>
                <span style='font-size: 125%;'>
                Area <b>%{customdata[1]}</b></span>"""
            )
            + "<extra></extra>",  # removes trace name box on the right
            customdata=(
                df[
                    [
                        "id",
                        "description",
                        "latitude",
                        "longitude",
                        "period_start",
                        "period_end",
                    ]
                ]
                if spatial_granularity == "location"
                else df[["id", "area_label", "period_start", "period_end"]]
            ),
        ),
        layout=go.Layout(
            hovermode="closest",
            xaxis={
                "type": "date",
                "ticklabelmode": "period",
                "dtick": dtick_setting,
                "tickformat": format_setting,
            },
            yaxis={
                "tickmode": "array",
                "tickvals": df["id"],
                "ticktext": df["description"],
            },
            # horizontal leyend above chart if aqi scale/categories shown
            legend={
                "orientation": "h",  # horizontal layout
                "yanchor": "bottom",
                "y": 1.02,  # above the top boundary of the heatmap
                "xanchor": "center",
                "x": 0.5,  # center horizontally
            },
        ),
    )

    if show_aqi_scale:
        for _, row in aqi_scale_df.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker={"size": 12, "color": row["color_hex"], "symbol": "square"},
                    name=row["categoria"] + " (" + row["category"] + ")",
                    showlegend=True,
                )
            )

    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    return fig


def aqi_scale():
    aqi_scale_df = fetch_aqi_scale()
    max_overall_aqi = aqi_scale_df["max_aqi"].max()
    custom_colorscale = []
    for _, row in aqi_scale_df.iterrows():
        # normalize bounds
        low_norm = row["min_aqi"] / max_overall_aqi
        high_norm = row["max_aqi"] / max_overall_aqi

        # pairs of [normalized_value, color] define color blocks
        custom_colorscale.append([low_norm, row["color_hex"]])
        custom_colorscale.append([high_norm, row["color_hex"]])

    return aqi_scale_df, custom_colorscale, max_overall_aqi


def timescale_params(temporal_granularity):
    format_setting = "%b\n%Y"

    match temporal_granularity:
        case "day":
            period_setting = 24 * 60 * 60 * 1000  # "D1"
            dtick_setting = "M6"
        case "week":
            period_setting = 7 * 24 * 60 * 60 * 1000  # in ms
            dtick_setting = "M4"
        case "month":
            period_setting = 30 * 24 * 60 * 60 * 1000  # "M1"
            dtick_setting = "M2"
        case _:
            raise ValueError

    return period_setting, dtick_setting, format_setting


def value_column(value):
    return value
