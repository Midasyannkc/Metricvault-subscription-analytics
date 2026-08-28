
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_created_date
from "metricvault"."main_staging"."stg_stripe__customers"
where customer_created_date is null



  
  
      
    ) dbt_internal_test