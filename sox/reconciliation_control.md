# Finance Reconciliation Control

This is the control that would actually get tested in a SOX audit of
this data product: does the ARR/MRR number the data team reports match
what Finance independently recorded, and is a discrepancy visible
rather than silently absorbed.

## Control objective

Detect, within one monthly close cycle, any variance between
Stripe-derived ARR (`fct_subscription_revenue`, built from event data)
and Finance's recorded ARR (`raw_finance.monthly_revenue_ledger`, an
independent source Analytics Engineering does not control), beyond a
2% threshold.

## Why 2%, and why independence matters

2% is a materiality threshold, not a technical one, small rounding and
timing differences (a GL entry posted a day into the next month, for
example) are expected and immaterial; anything larger indicates either
a data pipeline bug or a real, unreconciled business event (a manual
contract amendment, a refund processed outside Stripe, a plan change
that didn't sync). The control only works because the two numbers come
from genuinely independent sources: if the same team or system produced
both sides, a bug in the Stripe pipeline would silently propagate into
"Finance's" number too, and the reconciliation would always show PASS
regardless of whether the underlying number was actually right.

## What this repo's run actually found

Running the real reconciliation model (`dbt/models/marts/fct_finance_reconciliation.sql`)
against 18 months of data: **16 of 18 months reconcile within 2%. Two
months (2025-07 and 2026-03) fail the control**, at -3.7% and -2.5%
variance respectively. In this synthetic dataset, that's a deliberately
modeled one-time manual GL adjustment Finance booked directly (see
`dbt/scripts/load_raw_data.py`), the kind of real event a reconciliation
control exists to catch. In production, a FAIL here would trigger:

1. The Dagster `finance_reconciliation_check` asset check fires (see
   `dagster_project/assets.py`), visible in the pipeline run without
   blocking downstream BI refresh, a variance is a signal to
   investigate, not a reason to withhold the whole dashboard.
2. Analytics Engineering and Finance jointly investigate the specific
   month, tracing through `fct_mrr_movements` and the underlying Stripe
   events to find what the ledger captured that the pipeline didn't
   (or vice versa).
3. The finding is documented and either the pipeline is fixed (a real
   bug) or the variance is explained and accepted (a legitimate
   one-time entry), before that month's ARR is certified for the board
   deck or 10-Q.

## Verification

The actual query result, run against the real dbt-built table:

```
month        data_team_arr   finance_arr   variance_pct   control_status
2025-07-01   803,736.12      834,503.86    -3.69%         FAIL
2026-03-01   2,185,785.48    2,242,226.92  -2.52%         FAIL
(16 other months, all within +/-0.9%)                     PASS
```

Full output in `data/computed_kpis/finance_reconciliation.csv`.
