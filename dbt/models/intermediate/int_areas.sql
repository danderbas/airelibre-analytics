select *
from {{ ref('int_areas_limited') }}

union all

select
    max(area_id)+1 area_id,
    'Paraguay' area_label,
    null
from {{ ref('int_areas_limited') }}