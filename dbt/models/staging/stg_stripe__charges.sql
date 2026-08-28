with source as (
    select * from {{ source('stripe', 'charges') }}
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
