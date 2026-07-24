with areas_durations as (
    select
        area_id,
        min(dt) first_dt,
        max(dt) last_dt,
        date_diff('day', min(dt), max(dt))/30.42 as lifespan_months
    from {{ ref('int_areas_avg_aqi_grid') }}
    group by area_id
)

select
    location_id id,
    'location' spatial_grain,
    device_id,
    device_type,
    description,
    latitude,
    longitude,
    area_label,
    first_dt,
    last_dt,
    lifespan_days/30.42 lifespan_months,
    coverage_pct,
from {{ ref('dim_locations') }}
join {{ ref('fct_locations_quality') }}
using (location_id)

union all

select
    area_id id,
    'area' spatial_grain,
    null device_id,
    null device_type,
    area_label description,
    null latitude,
    null longitude,
    area_label,
    first_dt,
    last_dt,
    lifespan_months,
    null coverage_pct, -- can be calculated but wont
from {{ ref('int_areas')}}
join areas_durations
using (area_id)