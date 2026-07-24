select
    location_id,
    count(*) as actual_rows,
    date_diff('hour', min(dt), max(dt)) + 1 as expected_rows
from {{ ref('int_locations_aqi_grid') }}
group by 1
having count(*) != expected_rows