with source as (
    select * from "metricvault"."raw_stripe"."refunds"
),

renamed as (
    select
        refund_id,
        charge_id,
        cast(amount as double) as refund_amount,
        reason as refund_reason,
        cast(created as date) as refund_created_date
    from source
)

select * from renamed