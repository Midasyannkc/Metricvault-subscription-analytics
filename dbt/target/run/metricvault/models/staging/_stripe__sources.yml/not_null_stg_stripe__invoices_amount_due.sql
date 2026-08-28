
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select amount_due
from "metricvault"."main_staging"."stg_stripe__invoices"
where amount_due is null



  
  
      
    ) dbt_internal_test