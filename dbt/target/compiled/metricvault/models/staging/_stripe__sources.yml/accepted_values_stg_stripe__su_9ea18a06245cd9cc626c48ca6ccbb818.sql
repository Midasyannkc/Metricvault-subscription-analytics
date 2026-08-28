
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "metricvault"."main_staging"."stg_stripe__subscriptions"
    group by status

)

select *
from all_values
where value_field not in (
    'active','canceled'
)


