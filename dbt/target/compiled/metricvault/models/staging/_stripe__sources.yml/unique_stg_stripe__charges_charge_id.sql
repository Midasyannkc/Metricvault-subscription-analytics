
    
    

select
    charge_id as unique_field,
    count(*) as n_records

from "metricvault"."main_staging"."stg_stripe__charges"
where charge_id is not null
group by charge_id
having count(*) > 1


