-- Staging: one-to-one with the raw Stripe Customer object landed in
-- RAW.STRIPE.CUSTOMERS by the Dagster stripe_extract asset. No business
-- logic here, only typing and renaming, per dbt staging conventions.

with source as (
    select * from "metricvault"."raw_stripe"."customers"
),

renamed as (
    select
        customer_id,
        cast(created as date)      as customer_created_date,
        country,
        signup_channel
    from source
)

select * from renamed