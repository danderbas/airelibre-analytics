/* 
areas are (non-overlapping) concentric rings,
defined as a function of distance for asuncion centro (capital city's downtown)
(thresholds generated from seed csv data)
*/
select
    row_number() over (order by max_distance_from_asucentro_km asc) as area_id,
    area_label,
    max_distance_from_asucentro_km
from {{ ref('area_thresholds') }}