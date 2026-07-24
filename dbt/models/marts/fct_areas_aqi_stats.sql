with aqi_stats as (
    select
        area_id,
        count(avg_aqi) as count,
        min(avg_aqi) as min_aqi,
        max(avg_aqi) as max_aqi,
        median(avg_aqi) as median_aqi,
        quantile_cont(avg_aqi, 0.9) AS p90_aqi,
        avg(avg_aqi) as avg_aqi,
        stddev(avg_aqi) as std_aqi
    from {{ ref('int_areas_avg_aqi_grid') }}
    group by area_id
)
select
    area_id,
    s.count,
    s.min_aqi,
    s.max_aqi,
    s.median_aqi,
    round(s.p90_aqi, 1) p90_aqi,
    round(s.avg_aqi, 1) avg_aqi,
    round(s.std_aqi, 1) std_aqi
from aqi_stats s