-- Monthly customer-level MRR snapshot. This is what Net Revenue
-- Retention and Logo Retention cohort metrics read from: "what was
-- this customer's MRR in month N vs. their cohort's starting MRR."
--
-- IMPORTANT modeling note: a naive cumulative sum over
-- fct_mrr_movements only produces a row for months where a customer
-- HAD a movement, which silently drops every customer from the
-- snapshot in every month after their last event, understating active
-- MRR badly the longer the history runs. The fix is a full
-- customer x month spine with the cumulative sum computed over every
-- month, not just movement months, then forward-filled implicitly by
-- the window frame.



with movements as (
    select * from "metricvault"."main_marts"."fct_mrr_movements"
),

month_spine as (
    select distinct movement_month as spine_month from movements
),

customer_first_month as (
    select customer_id, min(movement_month) as first_month
    from movements
    group by 1
),

-- every (customer, month) pair from the customer's first event month
-- through the end of the observed spine, whether or not that customer
-- had an event in that specific month
customer_month_spine as (
    select c.customer_id, m.spine_month
    from customer_first_month c
    join month_spine m on m.spine_month >= c.first_month
),

monthly_deltas as (
    select customer_id, movement_month, sum(mrr_delta) as month_delta
    from movements
    group by 1, 2
),

spine_with_deltas as (
    select
        s.customer_id,
        s.spine_month,
        coalesce(d.month_delta, 0) as month_delta
    from customer_month_spine s
    left join monthly_deltas d
        on s.customer_id = d.customer_id and s.spine_month = d.movement_month
)

select
    customer_id,
    spine_month as snapshot_month,
    round(sum(month_delta) over (
        partition by customer_id order by spine_month
        rows between unbounded preceding and current row
    ), 2) as mrr_usd,
    case when sum(month_delta) over (
        partition by customer_id order by spine_month
        rows between unbounded preceding and current row
    ) > 0 then true else false end as is_active
from spine_with_deltas