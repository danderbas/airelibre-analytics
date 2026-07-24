select
    lsid location_id,
    dt,
    aqi
from {{ source('core', 'readings') }}