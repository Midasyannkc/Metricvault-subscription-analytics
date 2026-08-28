
  
  create view "metricvault"."main_intermediate"."int_mrr_movements__dbt_tmp" as (
    -- This is the core analytical logic of the entire project: classifying
-- every month-over-month MRR change into new / expansion / contraction
-- / churned / reactivation, the categories that make an MRR bridge
-- (waterfall) chart possible and that every SaaS board deck relies on.
--
-- Grain: one row per customer per calendar month in which their MRR
-- changed (a customer with no change in a given month does not appear
-- here; fct_subscription_revenue in the marts layer carries the
-- steady-state "unchanged" rows).

with subscriptions as (
    select * from "metricvault"."main_staging"."stg_stripe__subscriptions"
),

plan_changes as (
    select * from "metricvault"."main_staging"."stg_stripe__plan_changes"
),

plan_mrr as (
    select * from "metricvault"."main_marts"."dim_plan"
),

-- new: first-ever active subscription for a customer
new_events as (
    select
        customer_id,
        date_trunc('month', subscription_start_date) as movement_month,
        'new' as movement_type,
        pm.monthly_mrr_usd as mrr_delta
    from subscriptions s
    join plan_mrr pm on s.plan_id = pm.plan_id
    where s.status = 'active'
    qualify row_number() over (partition by s.customer_id order by s.subscription_start_date) = 1
),

-- churned: subscription canceled, MRR delta is the full negative amount
churn_events as (
    select
        customer_id,
        date_trunc('month', subscription_canceled_date) as movement_month,
        'churned' as movement_type,
        -1 * pm.monthly_mrr_usd as mrr_delta
    from subscriptions s
    join plan_mrr pm on s.plan_id = pm.plan_id
    where s.status = 'canceled'
),

-- expansion / contraction: plan changes, sign of mrr_delta determines direction
plan_change_events as (
    select
        customer_id,
        date_trunc('month', change_date) as movement_month,
        case when mrr_delta > 0 then 'expansion' else 'contraction' end as movement_type,
        mrr_delta
    from plan_changes
),

-- reactivation: a "new" event for a customer who has a prior churn event
-- before it, reclassified from 'new' to 'reactivation'
combined as (
    select * from new_events
    union all
    select * from churn_events
    union all
    select * from plan_change_events
),

reclassified as (
    select
        customer_id,
        movement_month,
        case
            when movement_type = 'new'
                 and exists (
                     select 1 from churn_events c
                     where c.customer_id = combined.customer_id
                       and c.movement_month < combined.movement_month
                 )
                then 'reactivation'
            else movement_type
        end as movement_type,
        mrr_delta
    from combined
)

select
    -- native surrogate key (avoids a dbt_utils package dependency for
    -- this repo; dbt_utils.generate_surrogate_key is the equivalent
    -- production choice and is a drop-in swap)
    md5(cast(customer_id as varchar) || '-' || cast(movement_month as varchar) || '-' || movement_type) as movement_id,
    customer_id,
    movement_month,
    movement_type,
    mrr_delta
from reclassified
  );
