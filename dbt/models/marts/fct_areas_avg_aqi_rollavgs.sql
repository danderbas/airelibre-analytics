select
    area_id,
    dt,
    avg_aqi as aqi,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24/2 preceding
        and 24/2-1 following
    ) as aqi_ravg_d,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24/2 preceding
        and 24/2-1 following
    ) as count_d,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 7*24/2 preceding
        and 24/2-1 following
    ) as aqi_ravg_w,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 7*24/2 preceding
        and 24/2-1 following
    ) as count_w,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 30*24/2 preceding
        and 30*24/2-1 following
    ) as aqi_ravg_m,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 30*24/2 preceding
        and 30*24/2-1 following
    ) as count_m

from {{ ref('int_areas_avg_aqi_grid') }}
order by area_id, dt
