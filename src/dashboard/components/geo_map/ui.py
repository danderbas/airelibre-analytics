import numpy as np
import plotly.graph_objects as go

from src.dashboard.utils.ui import hash_id_to_color


def render(df):
    # CENTER_LAT = -25.2968
    # CENTER_LON = -57.6350

    # this is the actual asucentro (punto cero)
    # -25.282107739481166, -57.6350526639851
    CENTER_LAT = -25.2821077
    CENTER_LON = -57.635053

    # get data from db!!!!

    AREAS = [
        {
            "label": "Macro Asunción",
            "radius_km": 60.0,
            "line_color": "rgba(0, 0, 255, 1)",
            "fill_color": "rgba(0, 0, 255, 0.1)",
        },
        {
            "label": "Gran Asunción",
            "radius_km": 25.0,
            "line_color": "rgba(0, 255, 0, 1)",
            "fill_color": "rgba(0, 255, 0, 0.1)",
        },
        {
            "label": "Asunción",
            "radius_km": 8,  # 10.0,
            "line_color": "rgba(255, 0, 0, 1)",
            "fill_color": "rgba(255, 0, 0, 0.1)",
        },
    ]

    fig = go.Figure()

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

    fig.add_trace(
        go.Scattermap(
            lat=df["latitude"],
            lon=df["longitude"],
            mode="markers",
            marker={"size": 12, "color": df["location_id"].apply(hash_id_to_color)},
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "id: %{customdata[1]}<br>"
                "tipo: %{customdata[2]}<br>"
                "zona: %{customdata[3]}<br>"
                "<br>(%{customdata[4]}, %{customdata[5]})"
                "<extra></extra>"  # removes trace name box on the right
            ),
            customdata=df[  # hovertemplate's custom data
                [
                    "description",
                    "location_id",
                    "device_type",
                    "area_label",
                    "latitude",
                    "longitude",
                ]
            ].values,
        )
    )

    fig.update_layout(
        map={
            "style": "open-street-map",
            "center": {"lat": CENTER_LAT, "lon": CENTER_LON},
            "zoom": 5.5,
        },
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
