-- This is THE certified table behind the ARR/MRR bridge chart every
-- SaaS board deck uses. One row per customer per month per movement
-- type. MetricFlow's mrr_movement metric group (see
-- semantic_layer/metrics.yml) reads from this table exclusively, so
-- there is exactly one definition of "expansion MRR" anywhere in the
-- company, here.



select
    movement_id,
    customer_id,
    movement_month,
    movement_type,
    mrr_delta
from "metricvault"."main_intermediate"."int_mrr_movements"