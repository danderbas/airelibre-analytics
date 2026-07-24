select
    location_id,
    unnest(
        generate_series(
            first_dt,
            last_dt,
            interval '{{ var("delta_dt_h") }} hour'
        )
    ) as dt
from {{ ref('int_locations_bounds') }}
order by location_id, dt