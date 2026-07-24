select
    located_sensor_id as location_id,
    device_id,
    sensor_type as device_type,
    sensor_desc as description,
    lat as latitude,
    lon as longitude,
    first_start_dt as first_dt,
    last_end_dt
      - interval '{{ var("delta_dt_h") }} hour'
      as last_dt
from {{ source('core', 'dim_sensors' )}}
