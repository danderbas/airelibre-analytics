select
    area_id,
    area_label,
    max_distance_from_asucentro_km
from {{ ref('int_areas') }}
order by area_id