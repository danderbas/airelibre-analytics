with avg_aqi_stats as (
    select
        area_id,
        min(avg_aqi) as min_avg_aqi,
        max(avg_aqi) as max_avg_aqi,
        median(avg_aqi) as median_avg_aqi,
        avg(avg_aqi) as avg_avg_aqi,
        stddev(avg_aqi) as std_avg_aqi
    from {{ ref('int_areas_avg_aqi_grid') }} r
    group by area_id
),
areas as (
    select
        area_id,
        area_label
    from {{ ref('int_areas') }}
)
select
    area_id,
    a.area_label,
    --d.first_dt,
    --d.last_dt
    s.min_avg_aqi,
    s.max_avg_aqi,
    s.median_avg_aqi,
    round(s.avg_avg_aqi, 1) avg_avg_aqi,
    round(s.std_avg_aqi, 1) std_avg_aqi
from avg_aqi_stats s
join areas a using (area_id)
