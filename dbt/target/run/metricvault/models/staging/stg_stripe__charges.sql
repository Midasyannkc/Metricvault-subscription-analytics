
  
  create view "metricvault"."main_staging"."stg_stripe__charges__dbt_tmp" as (
    with source as (
    select * from "metricvault"."raw_stripe"."charges"
),

renamed as (
    select
        charge_id,
        invoice_id,
        customer_id,
        cast(amount as double) as amount,
        status,
        cast(created as date) as charge_created_date
    from source
)

select * from renamed
  );
