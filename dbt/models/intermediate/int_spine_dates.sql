with daily as (
    select
        location_id,
        unnest(
            generate_series(
                date_trunc('day', first_dt),
                date_trunc('day', last_dt),
                interval '1 day'
            )
        )::date as d,
        'day' as granularity
    from {{ ref('int_locations_bounds') }}
),
weekly as (
    select
        location_id,
        unnest(
            generate_series(
                date_trunc('week', first_dt),
                date_trunc('week', last_dt),
                interval '1 week'
            )
        )::DATE as d,
        'week' as granularity
    from {{ ref('int_locations_bounds') }}
),
monthly as (
    select
        location_id,
        unnest(
            generate_series(
                date_trunc('month', first_dt),
                date_trunc('month', last_dt),
                interval '1 month'
            )
        )::DATE as d,
        'month' as granularity
    from {{ ref('int_locations_bounds') }}
)

select * from daily

union all

select * from weekly

union all

select * from monthly

order by granularity, location_id, d
