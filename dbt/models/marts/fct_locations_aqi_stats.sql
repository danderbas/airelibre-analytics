with aqi_stats as (
    select
        location_id,
        count(*) as expected_readings,
        count(aqi) as actual_readings,
        1.0 * count(aqi) / count(*) as coverage,
        min(aqi) as min_aqi,
        max(aqi) as max_aqi,
        median(aqi) as median_aqi,
        avg(aqi) as avg_aqi,
        stddev(aqi) as std_aqi
    from {{ ref('int_locations_aqi_grid') }}
    group by location_id
),
duration as (
    select
        location_id,
        first_dt,
        last_dt,
        date_diff('day', first_dt, last_dt) as lifespan_days
    from {{ ref('int_locations_bounds') }}
)
select
    location_id,
    d.first_dt,
    d.last_dt,
    d.lifespan_days,
    s.expected_readings,
    s.actual_readings,
    round(100 * s.coverage, 1) as coverage_pct,
    round(s.coverage, 4) as coverage_frac,
    s.min_aqi,
    s.max_aqi,
    s.median_aqi,
    round(s.avg_aqi, 1) avg_aqi,
    round(s.std_aqi, 1) std_aqi
from aqi_stats s
join duration d using (location_id)