select
    area_id,
    area_label,
    dt,
    avg_aqi,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*1-1 preceding and current row
    ) as avg_aqi_ravg_d,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*1-1 preceding and current row
    ) as count_d,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*7-1 preceding and current row
    ) as avg_aqi_ravg_w,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*7-1 preceding and current row
    ) as count_w,

    avg(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*30-1 preceding and current row
    ) as avg_aqi_ravg_m,
    count(avg_aqi) over (
        partition by area_id
        order by dt
        rows between 24*30-1 preceding and current row
    ) as count_m
from {{ ref('int_areas_avg_aqi_grid') }}
join {{ ref('int_areas') }} using (area_id)