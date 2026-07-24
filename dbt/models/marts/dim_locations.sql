with locations as (
    select
        location_id,
        latitude,
        longitude,
        area_label,
        area_id
    from {{ ref('int_locations_areas') }}
)
select
    location_id,
    s.device_id,
    s.device_type,
    s.description,
    l.latitude,
    l.longitude,
    l.area_label,
    l.area_id,
from {{ ref('stg_locations') }} s
join locations l using (location_id)