
    
    

select
    refund_id as unique_field,
    count(*) as n_records

from "metricvault"."main_staging"."stg_stripe__refunds"
where refund_id is not null
group by refund_id
having count(*) > 1


