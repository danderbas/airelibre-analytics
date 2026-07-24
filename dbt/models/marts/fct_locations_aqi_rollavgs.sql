select
    location_id,
    dt,
    aqi,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 24/2 preceding
        and 24/2-1 following
    ) as aqi_ravg_d,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 24/2 preceding
        and 24/2-1 following
    ) as count_d,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 7*24/2 preceding
        and 24/2-1 following
    ) as aqi_ravg_w,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 7*24/2 preceding
        and 24/2-1 following
    ) as count_w,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 30*24/2 preceding
        and 30*24/2-1 following
    ) as aqi_ravg_m,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 30*24/2 preceding
        and 30*24/2-1 following
    ) as count_m
from {{ ref('int_locations_aqi_grid') }}
join {{ ref('int_locations_valid') }} using (location_id)
where is_valid = true
order by location_id, dt