select
    a.area_id,
    l.dt,
    avg(l.aqi) avg_aqi,
    count(location_id) contributing_locations
from {{ ref('int_locations_aqi_grid') }} l
join {{ ref('int_locations_areas') }} a
    using (location_id)
join {{ ref('int_locations_valid') }} using (location_id)
where is_valid = true
group by 1, 2
order by area_id, dt