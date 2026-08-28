
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select mrr_usd
from "metricvault"."main_marts"."fct_subscription_revenue"
where mrr_usd is null



  
  
      
    ) dbt_internal_test