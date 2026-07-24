def hash_id_to_color(x):
    return f"hsl({int(2 * x, 16) % 360}, 85%, 55%)"
