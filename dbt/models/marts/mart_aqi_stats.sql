select
    location_id id,
    'location' spatial_grain,
    d.description,
    d.latitude,
    d.longitude,
    d.area_label,
    period_start,
    period_end,
    granularity time_grain,
    count,
    min_aqi,
    max_aqi,
    median_aqi,
    p90_aqi,
    avg_aqi,
    std_aqi
from {{ ref('fct_locations_aqi_periods_stats')}}
join {{ ref('dim_locations') }} d
using (location_id)

union all

select
    area_id,
    'area' spatial_grain,
    a.area_label description,
    null latitude,
    null longitude,
    a.area_label,
    period_start,
    period_end,
    granularity time_grain,
    cumulative_count count,
    min_aqi,
    max_aqi,
    median_aqi,
    p90_aqi,
    avg_aqi,
    std_aqi
from {{ ref('fct_areas_avg_aqi_periods_stats')}}
join {{ ref('int_areas') }} a
using (area_id)
