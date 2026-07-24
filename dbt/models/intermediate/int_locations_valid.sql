with coverage as (
    select
        location_id,
        count(*) as expected_readings,
        count(aqi) as actual_readings,
        1.0 * count(aqi) / count(*) as coverage
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
    c.expected_readings,
    c.actual_readings,
    round(100 * c.coverage, 1) as coverage_pct,
    round(c.coverage, 4) as coverage_frac,
    coverage_frac >= {{ var('valid_params')['min_coverage_frac'] }}
        and actual_readings > {{ var('valid_params')['min_readings'] }}
        as is_valid
from coverage c
join duration d using (location_id)