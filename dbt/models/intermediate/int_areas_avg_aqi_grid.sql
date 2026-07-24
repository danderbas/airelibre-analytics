with recursive cum_areas as (
    select 
        area_id,
        dt,
        avg_aqi,
        contributing_locations,
        contributing_locations contributing_outer_locations
    from {{ ref('int_areas_rings_avg_aqi_grid') }}
    where area_id = 1

    union all

    select
        g.area_id,
        g.dt,
        case 
            when
                coalesce(g.contributing_locations, 0) = 0
                then c.avg_aqi
            else
                (
                    c.avg_aqi + (g.contributing_locations * g.avg_aqi)
                ) / (1 + g.contributing_locations)
        end
            as avg_aqi,
        coalesce(c.contributing_locations, 0)
            + coalesce(g.contributing_locations, 0)
            as contributing_locations,
        coalesce(g.contributing_locations, 0) as contribuing_outer_locations 
    from {{ ref('int_areas_rings_avg_aqi_grid') }} g
    inner join cum_areas c 
        on g.dt = c.dt 
        and g.area_id = c.area_id + 1 
)
select
    area_id,
    dt,
    avg_aqi,
    contributing_locations,
    contributing_outer_locations
from cum_areas