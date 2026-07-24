import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.ui import area_id_to_color, unit_row_to_color

from .query import fetch_areas


def render():
    config = st.session_state.config
    show_locations = config["map"]["show_locations"]
    show_areas = config["map"]["show_areas"]

    df = st.session_state.units
    fig = go.Figure()

    df = df[df["spatial_grain"] == "location"]  # to avoid messing up colors later
    # just in case nothing is selected, the (geo)map will be still shown
    fig.add_trace(
        go.Scattermap(
            lat=[],
            lon=[],
        )
    )

    # this is the actual asucentro (punto cero)
    # i'm gonna just leave this hardcoded here for now
    # (could pull it from dbt's yml... or set it on config.yml and have dbt pull that)
    CENTER_LAT = -25.282108
    CENTER_LON = -57.635053

    if show_areas:
        areas_df = fetch_areas()

        AREAS = [
            {
                "label": r["area_label"],
                "radius_km": r["max_distance_from_asucentro_km"],
                "line_color": area_id_to_color(r["area_id"], alpha=1),
                "fill_color": area_id_to_color(r["area_id"], alpha=0.1),
            }
            for _, r in areas_df.iterrows()
        ]

        # draws circles (dots and fill="toself" for coloring)
        # (from large to small, to ensure 'hoverability')
        for area in AREAS:
            c_lats, c_lons = get_circle_coordinates(
                CENTER_LAT, CENTER_LON, area["radius_km"]
            )

            fig.add_trace(
                go.Scattermap(
                    lat=c_lats,
                    lon=c_lons,
                    mode="lines",
                    line={"width": 0.5, "color": area["line_color"]},
                    fill="toself",  # inner-area shading
                    fillcolor=area["fill_color"],
                    name=f"{area['label']} ({area['radius_km']} km)",
                    hoverinfo="name",
                )
            )

    if show_locations:
        # draw (sensor unit) location markers
        fig.add_trace(
            go.Scattermap(
                lat=df["latitude"],
                lon=df["longitude"],
                mode="markers",
                # alpha for units shown or not, color for availability
                # , size for time alive?
                marker={
                    "size": 12,
                    "color": df.apply(unit_row_to_color, axis=1),
                },
                hovertemplate=(
                    "<span style='font-size: 2em'><b>%{customdata[0]}</b></span>"
                    "<br><br>"
                    "<span style='font-size: 1.5em'>%{customdata[3]|%Y/%b/%d}"
                    " – %{customdata[4]|%Y/%b/%d}</span><br><br>"
                    "<b>%{customdata[2]}%</b> coverage<br>"
                    "over <b>%{customdata[5]:.1f}</b> months<br><br>"
                    "<b>%{customdata[1]}</b> area<br>"
                    "(%{customdata[6]}, %{customdata[7]})<br>"
                    "id %{customdata[8]}"
                    "<extra></extra>"  # removes trace name box on the right
                ),
                customdata=df[  # hovertemplate's custom data
                    [
                        "description",
                        "area_label",
                        "coverage_pct",
                        "first_dt",
                        "last_dt",
                        "lifespan_months",
                        "latitude",
                        "longitude",
                        "id",
                    ]
                ].values,
                hoverlabel={"bordercolor": df.apply(unit_row_to_color, axis=1)},
            )
        )

    fig.update_layout(
        map={
            "style": "open-street-map",
            "center": {"lat": CENTER_LAT, "lon": CENTER_LON},
            "zoom": 5.5,
        },
        # hovermode="x unified",
        showlegend=False,
        margin={"l": 5, "r": 15, "t": 20, "b": 20},
        shapes=[
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": 0,
                "y0": 0,
                "x1": 1,
                "y1": 1,
                "line": {
                    "color": "#AAAAAA",  # Border color (e.g., light gray)
                    "width": 1,  # Border thickness
                },
            }
        ],
    )

    return fig


def get_circle_coordinates(center_lat, center_lon, radius_km, num_points=100):
    """to draw area-enclosing circles"""
    earth_radius_km = 6371.0
    lat_rad = np.radians(center_lat)
    lon_rad = np.radians(center_lon)
    angular_dist = radius_km / earth_radius_km
    angles = np.linspace(0, 2 * np.pi, num_points)

    circle_lats = []
    circle_lons = []
    for angle in angles:
        c_lat = np.arcsin(
            np.sin(lat_rad) * np.cos(angular_dist)
            + np.cos(lat_rad) * np.sin(angular_dist) * np.cos(angle)
        )
        c_lon = lon_rad + np.arctan2(
            np.sin(angle) * np.sin(angular_dist) * np.cos(lat_rad),
            np.cos(angular_dist) - np.sin(lat_rad) * np.sin(c_lat),
        )
        circle_lats.append(np.degrees(c_lat))
        circle_lons.append(np.degrees(c_lon))

    return circle_lats, circle_lons
