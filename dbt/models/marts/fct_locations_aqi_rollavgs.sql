select
    location_id,
    dt,
    aqi,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 24*1-1 preceding and current row
    ) as aqi_ravg_d,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 24*1-1 preceding and current row
    ) as count_d,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 24*7-1 preceding and current row
    ) as aqi_ravg_w,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 24*7-1 preceding and current row
    ) as count_w,

    avg(aqi) over (
        partition by location_id
        order by dt
        rows between 24*30-1 preceding and current row
    ) as aqi_ravg_m,
    count(aqi) over (
        partition by location_id
        order by dt
        rows between 24*30-1 preceding and current row
    ) as count_m
from {{ ref('int_locations_aqi_grid') }}