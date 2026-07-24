import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.ui import hash_id_to_color


def render(df: pd.DataFrame) -> go.Figure:
    config = st.session_state.config

    temporal_granularity = config["plot"]["granularity"]["temporal"]
    spatial_granularity = config["plot"]["granularity"]["spatial"]
    temporal_granularity_char = temporal_granularity[0]

    fig = go.Figure()

    for unit, group in df.groupby(
        "location_id" if spatial_granularity == "location" else "area_id"
    ):
        fig.add_trace(
            go.Scatter(
                x=group["dt"],
                y=group[
                    "aqi_ravg_" + temporal_granularity_char
                    if temporal_granularity != "hour"
                    else "aqi"
                ],
                mode="lines",
                name=str(unit),  # for legendL
                line={"width": 1, "color": hash_id_to_color(unit)},
                hovertemplate=(
                    f"<b>{unit}</b><br>Date: %{{x}}<br>AQI: %{{y:.1f}}<extra></extra>"
                ),
                # hovertemplate=(
                #    # "<b>%{customdata[0]}</b><br><br>"
                #    "id: %{customdata[0]}<br>"
                #    # "tipo: %{customdata[2]}<br>"
                #    # "zona: %{customdata[3]}<br>"
                #    # "<br>(%{customdata[4]},%{customdata[5]})"
                #    "<extra></extra>"  # removes trace name box on the right
                # ),
                # customdata=df[  # hovertemplate's custom data
                #    ["location_id" if spatial_granularity == "location" else "area_id"]
                # ].values,
                # => too much for this plot
            )
        )

    fig.update_layout(
        xaxis={"type": "date"},
        yaxis={
            "title": "AQI",
            "gridcolor": "rgba(0,0,0,0.1)",  # light gridlines
        },
        hovermode="closest",
        showlegend=False,  # might show if less than N (5?) curves are shown...
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    fig.update_layout(showlegend=False)

    return fig
