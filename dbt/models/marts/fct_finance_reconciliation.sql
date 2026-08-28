-- SOX-relevant reconciliation: compares the data team's ARR (derived
-- from Stripe events via fct_mrr_movements) against Finance's
-- independently-recorded revenue ledger (synthetic stand-in for a
-- NetSuite GL export). A variance beyond threshold on this model is
-- exactly the kind of control failure that would block a financial
-- close in a real public-company environment.
--
-- Source for finance_ledger: {{ source('finance', 'monthly_revenue_ledger') }}
-- landed via a separate, Finance-owned ingestion (out of scope for
-- this repo, see sox/reconciliation_control.md for the control design).

{{ config(materialized='table') }}

with data_team_arr as (
    select
        snapshot_month as month,
        sum(mrr_usd) * 12 as data_team_arr_usd
    from {{ ref('fct_subscription_revenue') }}
    group by 1
),

finance_ledger as (
    select
        ledger_month as month,
        recorded_arr_usd as finance_arr_usd
    from {{ source('finance', 'monthly_revenue_ledger') }}
)

select
    d.month,
    d.data_team_arr_usd,
    f.finance_arr_usd,
    d.data_team_arr_usd - f.finance_arr_usd as variance_usd,
    round((d.data_team_arr_usd - f.finance_arr_usd) / nullif(f.finance_arr_usd, 0), 4) as variance_pct,
    case
        when abs((d.data_team_arr_usd - f.finance_arr_usd) / nullif(f.finance_arr_usd, 0)) > 0.02
            then 'FAIL: exceeds 2% control threshold'
        else 'PASS'
    end as control_status
from data_team_arr d
join finance_ledger f using (month)
order by d.month
