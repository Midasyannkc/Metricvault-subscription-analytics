{{ config(materialized='table') }}

select
    c.customer_id,
    c.customer_created_date,
    c.country,
    c.signup_channel,
    min(s.subscription_start_date) as first_subscription_date
from {{ ref('stg_stripe__customers') }} c
left join {{ ref('stg_stripe__subscriptions') }} s using (customer_id)
group by 1, 2, 3, 4
