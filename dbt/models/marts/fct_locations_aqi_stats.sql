with aqi_stats as (
    select
        location_id,
        min(aqi) as min_aqi,
        max(aqi) as max_aqi,
        median(aqi) as median_aqi,
        avg(aqi) as avg_aqi,
        stddev(aqi) as std_aqi
    from {{ ref('int_locations_aqi_grid') }}
    group by location_id
)
select
    location_id,
    s.min_aqi,
    s.max_aqi,
    s.median_aqi,
    round(s.avg_aqi, 1) avg_aqi,
    round(s.std_aqi, 1) std_aqi
from aqi_stats s
join {{ ref('int_locations_valid') }} using (location_id)
where is_valid = true