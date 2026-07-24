from .aqi_heatmap.query import fetch as fetch_aqi_heatmap
from .aqi_heatmap.ui import render as render_aqi_heatmap
from .aqi_plot.query import fetch as fetch_aqi_plot
from .aqi_plot.ui import render as render_aqi_plot
from .geo_map.query import fetch as fetch_geo_map
from .geo_map.ui import render as render_geo_map


def aqi_heatmap():
    df = fetch_aqi_heatmap()
    fig = render_aqi_heatmap(df)
    return fig


def aqi_plot():
    df = fetch_aqi_plot()
    fig = render_aqi_plot(df)
    return fig


def geo_map():
    df = fetch_geo_map()
    return render_geo_map(df)