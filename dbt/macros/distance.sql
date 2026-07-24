-- haversine distance (euclidean would have been enough XD)
{% macro distance(lat1, lon1, lat2, lon2) %}
    (2 * 6371 * asin(sqrt(
        pow(sin((radians({{ lat1 }}) - radians({{ lat2 }})) / 2), 2) +
        cos(radians({{ lat2 }})) * cos(radians({{ lat1 }})) *
        pow(sin((radians({{ lon1 }}) - radians({{ lon2 }})) / 2), 2)
    )))
{% endmacro %}