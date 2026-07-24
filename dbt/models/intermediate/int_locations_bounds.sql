select
    location_id,
    min(dt) as first_dt,
    max(dt) as last_dt
from {{ ref('stg_locations_aqi') }}
group by 1
