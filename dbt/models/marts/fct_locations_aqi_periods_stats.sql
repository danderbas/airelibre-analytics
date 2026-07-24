with period_intervals as (
    select
        location_id,
        d period_start,
        lead(d) over (
            partition by location_id, granularity
            order by d
        ) as period_end,
        granularity
    from {{ ref('int_spine_dates') }}
),
aqi_stats as (
    select
        s.location_id,
        s.period_start,
        s.period_end,
        s.granularity,
        --count(*) as expected_readings,
        count(r.aqi) as count,--_readings,
        1.0 * count(r.aqi) / count(*) as coverage,
        median(r.aqi) as median_aqi,
        quantile_cont(r.aqi, 0.9) AS p90_aqi,
        min(r.aqi) as min_aqi,
        max(r.aqi) as max_aqi,
        avg(r.aqi) as avg_aqi,
        stddev(r.aqi) as std_aqi,
    from period_intervals as s
    left join {{ ref('int_locations_aqi_grid') }} r
        on s.location_id = r.location_id
            and s.period_start <= r.dt::date
            and r.dt::date < s.period_end
    where s.period_end is not null
    group by s.location_id, s.period_start, s.period_end, s.granularity
)
select
    location_id,
    period_start,
    period_end,
    granularity,
    count,
    min_aqi,
    max_aqi,
    round(median_aqi, 1) median_aqi,
    round(p90_aqi, 1) p90_aqi,
    round(avg_aqi, 1) avg_aqi,
    round(std_aqi, 1) std_aqi,
    round(100 * coverage, 1) as coverage_pct,
    round(coverage, 4) as coverage_frac
from aqi_stats s
join {{ ref('int_locations_valid') }} using (location_id)
where is_valid = true