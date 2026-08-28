-- Plan dimension. Small enough to be a dbt seed in production
-- (seeds/plan_reference.csv), modeled here as a model for clarity in
-- this repo. Monthly-normalized MRR is the key derived column: annual
-- plans are divided by 12 so ARR/MRR math is consistent regardless of
-- billing interval, the single most common subscription-analytics bug
-- when this normalization is skipped.

{{ config(materialized='table') }}

select * from (
    values
        ('price_free', 'Free', 0.0, 'month', 0.0),
        ('price_starter_m', 'Starter Monthly', 9.0, 'month', 9.0),
        ('price_starter_y', 'Starter Annual', 90.0, 'year', 7.5),
        ('price_pro_m', 'Pro Monthly', 29.0, 'month', 29.0),
        ('price_pro_y', 'Pro Annual', 290.0, 'year', 24.17),
        ('price_business_m', 'Business Monthly', 99.0, 'month', 99.0),
        ('price_business_y', 'Business Annual', 990.0, 'year', 82.5),
        ('price_enterprise_m', 'Enterprise Monthly', 299.0, 'month', 299.0)
) as t(plan_id, plan_name, list_price_usd, billing_interval, monthly_mrr_usd)
