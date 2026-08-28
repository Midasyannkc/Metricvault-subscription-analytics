
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select charge_id
from "metricvault"."main_staging"."stg_stripe__charges"
where charge_id is null



  
  
      
    ) dbt_internal_test