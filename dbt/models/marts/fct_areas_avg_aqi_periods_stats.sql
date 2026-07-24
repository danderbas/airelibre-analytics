with area_spines as (
    select distinct
        a.area_id,
        s.d,
        s.granularity
    from {{ ref('int_spine_dates') }} s
    join {{ ref('int_locations_areas') }} a
        using (location_id)
),
period_intervals as (
    select
        area_id,
        d period_start,
        lead(d) over (
            partition by area_id, granularity
            order by d
        ) as period_end,
        granularity
    from area_spines
),
avg_aqi_stats as (
    select
        s.area_id,
        s.period_start,
        s.period_end,
        s.granularity,
        sum(r.contributing_locations)
            as count,
        sum(r.contributing_total_locations)
            as cumulative_count,
        min(r.avg_aqi) as min_avg_aqi,
        max(r.avg_aqi) as max_avg_aqi,
        median(r.avg_aqi) as median_avg_aqi,
        quantile_cont(r.avg_aqi, 0.9) as p90_avg_aqi,
        avg(r.avg_aqi) as avg_avg_aqi,
        stddev(r.avg_aqi) as std_avg_aqi
    from period_intervals as s
    left join {{ ref('int_areas_avg_aqi_grid') }} r
        on s.area_id = r.area_id
            and s.period_start <= r.dt
            and r.dt < s.period_end
    where s.period_end is not null
    group by s.area_id, s.period_start, s.period_end, s.granularity
),
areas as (
    select
        area_id,
        area_label
    from {{ ref('int_areas') }}
)
select
    area_id,
    a.area_label,
    s.period_start,
    s.period_end,
    s.granularity,
    s.count,
    s.cumulative_count,
    s.min_avg_aqi min_aqi,
    s.max_avg_aqi max_aqi,
    round(s.median_avg_aqi, 1) median_aqi,
    round(s.p90_avg_aqi, 1) p90_aqi,
    round(s.avg_avg_aqi, 1) avg_aqi,
    round(s.std_avg_aqi, 1) std_aqi
from avg_aqi_stats s
join areas a using (area_id)
