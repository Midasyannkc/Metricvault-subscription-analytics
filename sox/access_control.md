# Access Control & Segregation of Duties

Maps to SOX ITGC (IT General Controls) access-control objectives.
Written for a Snowflake production environment; the DuckDB verification
run in this repo uses a single local file and does not enforce these
grants, they're documented here as the actual production design.

## Schema-level access model

| Schema | Contains | Who can read | Who can write |
|---|---|---|---|
| `RAW` | Immutable Stripe/Finance source data, landed by Dagster | Data Engineering, Analytics Engineering (read-only) | Dagster's service account only |
| `STAGING` | Typed, renamed, untested-for-business-logic views | Analytics Engineering | dbt job runner (CI/CD service account) |
| `INTERMEDIATE` | MRR movement classification logic | Analytics Engineering | dbt job runner |
| `MART` | Certified tables (`fct_mrr_movements`, `fct_subscription_revenue`, `fct_finance_reconciliation`, dimensions) | All BI consumers (Tableau service account, Looker service account, ad hoc analyst read-only role) | dbt job runner only |

**No human user has direct write access to any schema.** All writes happen through the Dagster-orchestrated dbt job runner, authenticated as a dedicated service account with its own audit log. This is the core segregation-of-duties control: the person who can change a model definition (via PR) is never the same credential that executes the write.

## Segregation of duties

1. **Model changes** go through the change-management process in `change_management.md`, a PR reviewed by someone other than the author before merge.
2. **The merge** triggers CI, which runs `dbt build` under the service account, no human ever runs `dbt build` against production with personal credentials.
3. **Finance's ledger** (`raw_finance.monthly_revenue_ledger`) is landed by a separate ingestion process owned by Finance, not Analytics Engineering, so the reconciliation check in `fct_finance_reconciliation.sql` compares two independently-controlled data paths. If Analytics Engineering could also write the Finance side, the reconciliation wouldn't be a real control.

## RAW immutability as a control

The `RAW` schema is append-only. No `UPDATE` or `DELETE` grants exist on it for any role, including the ingestion service account (Dagster's `stripe_extract` asset only ever inserts new rows, keyed by Stripe's own object IDs, which are themselves immutable). This preserves the original source record indefinitely, the SOX-relevant property being that a number reported to the board can always be traced back to the exact source event that produced it, unaltered.
