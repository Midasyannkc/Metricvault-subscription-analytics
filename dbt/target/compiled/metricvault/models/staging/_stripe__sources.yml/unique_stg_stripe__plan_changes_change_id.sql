
    
    

select
    change_id as unique_field,
    count(*) as n_records

from "metricvault"."main_staging"."stg_stripe__plan_changes"
where change_id is not null
group by change_id
having count(*) > 1


