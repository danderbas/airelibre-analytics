with area_ranges as (
    select
        area_id,
        area_label,
        coalesce(
            lag(max_distance_from_asucentro_km)
                over (order by max_distance_from_asucentro_km asc), 
            0.0
        ) as min_distance_km,
        max_distance_from_asucentro_km max_distance_km
    from {{ ref('int_areas_limited') }}
),
locations_distance_from_asucentro as (
    select
        location_id,
        latitude,
        longitude,
        {{ 
            haversine_distance(
                'latitude',
                'longitude',
                var('loc_asucentro')['lat'],
                var('loc_asucentro')['lon']
            ) 
        }} as distance_from_asucentro_km
    from {{ ref('stg_locations') }}
)
select
    d.location_id,
    d.latitude,
    d.longitude,
    coalesce(r.area_id, max(r.area_id) over () + 1)
        as area_id,
    coalesce(r.area_label, 'interior')
        as area_label,
    round(d.distance_from_asucentro_km, 2)
        as dist_from_asucentro_km
from locations_distance_from_asucentro d
left join area_ranges r
    on d.distance_from_asucentro_km > r.min_distance_km
    and d.distance_from_asucentro_km <= r.max_distance_km
