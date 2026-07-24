import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.ui import area_id_to_color, hash_id_to_color


def render(df: pd.DataFrame) -> go.Figure:
    config = st.session_state.config

    temporal_granularity = config["plot"]["granularity"]["temporal"]
    spatial_granularity = config["granularity"]["spatial"].lower()
    temporal_granularity_char = temporal_granularity[0].lower()

    show_values = config["plot"]["show_values"]
    show_avg = config["plot"]["show_avg"]

    units: pd.DataFrame = (
        st.session_state.units  # .reset_index()
    )  # units visibility and info

    df = df[
        (df["spatial_grain"] == spatial_granularity)
        & (df["id"].isin(units[units["show"]]["id"]))
    ]

    fig = go.Figure()

    if show_values:
        for unit, group in df.groupby("id"):
            if units[units["id"] == unit]["show"].item():
                fig.add_trace(
                    go.Scatter(
                        x=group["dt"],
                        y=group[
                            "aqi_ravg_" + temporal_granularity_char
                            if temporal_granularity != "hour"
                            else "aqi"
                        ],
                        mode="lines",
                        name=str(group["description"].unique()[0]),  # for legend
                        line={
                            "width": 1.3 if spatial_granularity == "location" else 3,
                            "color": hash_id_to_color(unit)
                            if spatial_granularity == "location"
                            else area_id_to_color(int(unit)),
                        },
                        hovertemplate=(
                            """
                            <span style='font-size: 150%;'><b>%{y:.1f}</b> = AQI(%{x})</span>
                            <br><br>
                            <span style='font-size: 125%;'>
                            <b>%{customdata[1]}</b> (id %{customdata[0]})</span>
                            <br>(%{customdata[2]}, %{customdata[3]})"""
                            if spatial_granularity == "location"
                            else """
                            <span style='font-size: 150%;'><b>%{y:.1f}</b> = AQI(%{x})</span>
                            <br><br>
                            <span style='font-size: 125%;'>
                            Area <b>%{customdata[1]}</b></span>"""
                        )
                        + "<extra></extra>",  # removes trace name box on the right
                        customdata=(
                            group[["id", "description", "latitude", "longitude"]]
                            if spatial_granularity == "location"
                            else group[["id", "area_label"]]
                        ),
                        hoverlabel={
                            "bordercolor": (
                                hash_id_to_color(unit)
                                if spatial_granularity == "location"
                                else area_id_to_color(int(unit))
                            ),
                        },
                    )
                )

    if show_avg:
        try:
            theme_type = st.context.theme.type  # returns "light" or "dark"
        except (AttributeError, KeyError):
            theme_type = "light"

        avg = (
            df[
                [
                    "aqi_ravg_" + temporal_granularity_char
                    if temporal_granularity != "hour"
                    else "aqi",
                    "dt",
                ]
            ]
            .groupby("dt")
            .mean()
            .reset_index()
        )
        fig.add_trace(
            go.Scatter(
                x=avg["dt"],
                y=avg[
                    "aqi_ravg_" + temporal_granularity_char
                    if temporal_granularity != "hour"
                    else "aqi"
                ],
                mode="lines",
                name="Average AQI",  # for legend
                line={
                    "width": 2 if spatial_granularity == "location" else 3,
                    "color": "white" if theme_type == "dark" else "black",
                    # "dash": "dash",
                },
            )
        )

    fig.update_layout(
        xaxis={"type": "date"},
        yaxis={
            "title": "AQI",
            "gridcolor": "rgba(0,0,0,0.1)",  # light gridlines
        },
        hovermode="closest",
        showlegend=bool(
            (
                units[units["spatial_grain"] == spatial_granularity]["show"]
                .astype(int)
                .sum()
                if show_values
                else 0
            )
            + int(show_avg)
            <= 6
        ),  # show some, if few
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    return fig
