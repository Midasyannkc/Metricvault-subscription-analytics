
    
    

with all_values as (

    select
        control_status as value_field,
        count(*) as n_records

    from "metricvault"."main_marts"."fct_finance_reconciliation"
    group by control_status

)

select *
from all_values
where value_field not in (
    'PASS','FAIL: exceeds 2% control threshold'
)


