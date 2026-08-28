with source as (
    select * from {{ source('stripe', 'invoices') }}
),

renamed as (
    select
        invoice_id,
        customer_id,
        subscription_id,
        cast(period_start as date)  as period_start_date,
        cast(period_end as date)    as period_end_date,
        cast(amount_due as double) as amount_due,
        cast(amount_paid as double) as amount_paid,
        status,
        cast(created as date)       as invoice_created_date
    from source
)

select * from renamed
