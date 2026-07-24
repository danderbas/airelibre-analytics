select
    location_id,
    first_dt,
    last_dt,
    lifespan_days,
    expected_readings,
    actual_readings,
    coverage_pct,
    coverage_frac
from {{ ref('int_locations_valid') }}
where is_valid = true