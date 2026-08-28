with source as (
    select * from "metricvault"."raw_stripe"."subscriptions"
),

renamed as (
    select
        subscription_id,
        customer_id,
        plan_id,
        status,
        cast(start_date as date)                       as subscription_start_date,
        nullif(canceled_at, '')::date                  as subscription_canceled_date
    from source
)

select * from renamed