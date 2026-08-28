
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select invoice_id as from_field
    from "metricvault"."main_staging"."stg_stripe__charges"
    where invoice_id is not null
),

parent as (
    select invoice_id as to_field
    from "metricvault"."main_staging"."stg_stripe__invoices"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test