select
    s.location_id,
    s.dt,
    r.aqi
from {{ ref('int_spine_datetimes') }} s
left join {{ ref('stg_locations_aqi') }} r
    using (location_id, dt)