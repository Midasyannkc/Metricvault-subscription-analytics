
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select change_id
from "metricvault"."main_staging"."stg_stripe__plan_changes"
where change_id is null



  
  
      
    ) dbt_internal_test