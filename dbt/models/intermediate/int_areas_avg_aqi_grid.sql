with recursive full_disk as (
    select 
        area_id,
        dt,
        avg_aqi,
        contributing_locations,
        contributing_locations
            as contributing_total_locations
    from {{ ref('int_areas_rings_avg_aqi_grid') }}
    where area_id = 1

    union all

    select
        outer_shell.area_id,
        outer_shell.dt,
        case 
            when coalesce(outer_shell.contributing_locations, 0) = 0
                then inner_disk.avg_aqi
            else
                (
                    inner_disk.avg_aqi
                        + (outer_shell.contributing_locations
                            * outer_shell.avg_aqi)
                ) / (1 + outer_shell.contributing_locations)
        end as avg_aqi,
        coalesce(outer_shell.contributing_locations, 0)
            as contribuing_outer_locations,
        coalesce(inner_disk.contributing_total_locations, 0)
            + coalesce(outer_shell.contributing_locations, 0)
            as contributing__total_locations
    from {{ ref('int_areas_rings_avg_aqi_grid') }} as outer_shell
    inner join full_disk as inner_disk
        on outer_shell.dt = inner_disk.dt 
        and outer_shell.area_id = inner_disk.area_id + 1 
)
select
    area_id,
    dt,
    round(avg_aqi, 1) avg_aqi,
    contributing_locations,
    contributing_total_locations
from full_disk
order by area_id, dt