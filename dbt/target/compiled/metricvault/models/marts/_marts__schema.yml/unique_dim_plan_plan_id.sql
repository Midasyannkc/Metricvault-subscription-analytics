
    
    

select
    plan_id as unique_field,
    count(*) as n_records

from "metricvault"."main_marts"."dim_plan"
where plan_id is not null
group by plan_id
having count(*) > 1


