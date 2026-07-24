select
    a.area_id,
    l.dt,
    avg(l.aqi) avg_aqi,
    count(location_id) contributing_locations
from {{ ref('int_locations_aqi_grid') }} l
join {{ ref('int_locations_areas') }} a
    using (location_id)
group by 1, 2