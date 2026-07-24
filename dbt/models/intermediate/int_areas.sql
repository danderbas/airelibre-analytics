select *
from dev.int_areas_limited

union all

select
    max(area_id)+1 area_id,
    'paraguay' area_label,
    null
from dev.int_areas_limited