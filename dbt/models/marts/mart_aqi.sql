select
    location_id id,
    'location' spatial_grain,
    d.description,
    d.latitude,
    d.longitude,
    d.area_label,
    dt,
    aqi,
    aqi_ravg_d,
    count_d,
    aqi_ravg_w,
    count_w,
    aqi_ravg_m,
    count_m
from {{ ref('fct_locations_aqi_rollavgs') }}
join {{ ref('dim_locations') }} d
using (location_id)

union all

select
    area_id id,
    'area' spatial_grain,
    a.area_label description,
    null latitude,
    null longitude,
    a.area_label,
    dt,
    aqi,
    aqi_ravg_d,
    count_d,
    aqi_ravg_w,
    count_w,
    aqi_ravg_m,
    count_m
from {{ ref('fct_areas_avg_aqi_rollavgs') }}
join {{ ref('int_areas') }} a
using (area_id)
