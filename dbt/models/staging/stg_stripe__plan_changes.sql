with source as (
    select * from {{ source('stripe', 'plan_changes') }}
),

renamed as (
    select
        change_id,
        subscription_id,
        customer_id,
        cast(change_date as date)  as change_date,
        old_plan_id,
        new_plan_id,
        cast(old_mrr as double) as old_mrr,
        cast(new_mrr as double) as new_mrr,
        cast(new_mrr as double) - cast(old_mrr as double) as mrr_delta
    from source
)

select * from renamed
