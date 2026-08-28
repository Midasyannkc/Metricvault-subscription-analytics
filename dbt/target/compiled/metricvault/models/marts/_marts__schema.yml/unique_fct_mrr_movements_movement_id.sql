
    
    

select
    movement_id as unique_field,
    count(*) as n_records

from "metricvault"."main_marts"."fct_mrr_movements"
where movement_id is not null
group by movement_id
having count(*) > 1


