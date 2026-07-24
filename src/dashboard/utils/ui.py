import streamlit as st


def area_id_to_color(x, alpha=1):
    match x:
        case 1:
            return f"rgba(255, 0, 0, {alpha})"
        case 2:
            return f"rgba(0, 255, 0, {alpha})"
        case 3:
            return f"rgba(0, 0, 255, {alpha})"
        case 4:
            return f"rgba(0, 0, 0, {alpha})"
        case _:
            raise ValueError("no such area id")


def hash_id_to_color(x, alpha=1):
    return f"hsl({int(2 * x, 16) % 360}, 85%, 55%, {alpha})"


def unit_row_to_color(r):
    """
    alpha=1 for units shown and 0.2 for not shown,
    colored|gray for available|unavailable in selected time range
    """
    alpha = 1 if r["show"] else 0.5

    return (
        hash_id_to_color(r["id"], alpha)
        if r["in_selected_date_range"]
        else f"rgba(10,10,10,{alpha})"
    )


def toggle_show():
    """if not all on, then all on; if all on, then all off"""
    spatial_grain = st.session_state.config["granularity"]["spatial"].lower()
    df = st.session_state.units
    indices = st.session_state.units_index

    if len(
        df[
            (df["in_selected_date_range"])
            & (df["spatial_grain"] == spatial_grain)
            & (df["show"])
        ]
    ) != len(indices):
        df.loc[indices, "show"] = True
    else:
        df.loc[indices, "show"] = False
