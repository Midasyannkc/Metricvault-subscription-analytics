
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    movement_id as unique_field,
    count(*) as n_records

from "metricvault"."main_marts"."fct_mrr_movements"
where movement_id is not null
group by movement_id
having count(*) > 1



  
  
      
    ) dbt_internal_test