
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select charge_id as from_field
    from "metricvault"."main_staging"."stg_stripe__refunds"
    where charge_id is not null
),

parent as (
    select charge_id as to_field
    from "metricvault"."main_staging"."stg_stripe__charges"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test