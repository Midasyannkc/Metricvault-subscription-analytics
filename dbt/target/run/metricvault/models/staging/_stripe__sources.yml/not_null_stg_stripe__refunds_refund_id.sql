
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select refund_id
from "metricvault"."main_staging"."stg_stripe__refunds"
where refund_id is null



  
  
      
    ) dbt_internal_test