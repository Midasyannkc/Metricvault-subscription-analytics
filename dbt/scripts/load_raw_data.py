"""
Loads the synthetic Stripe CSVs into a DuckDB database under a
raw_stripe schema, and generates a synthetic Finance revenue ledger
(raw_finance schema) with a small, realistic variance from the
Stripe-derived numbers, so the reconciliation control in
fct_finance_reconciliation.sql has something real to check.

In production this step is the Dagster stripe_extract asset (writing
to Snowflake RAW) plus a separate Finance-owned NetSuite export job.
Collapsed into one script here because this repo runs the whole
pipeline locally against DuckDB for verification.

Run: python load_raw_data.py
Output: ../metricvault.duckdb
"""
import csv
import random
import duckdb
from datetime import date

random.seed(55)

DATA_DIR = "../../data"
DB_PATH = "../metricvault.duckdb"


def load_csv_to_table(con, schema, table, csv_path):
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    con.execute(f"CREATE OR REPLACE TABLE {schema}.{table} AS SELECT * FROM read_csv_auto('{csv_path}', ALL_VARCHAR=TRUE)")


def build_finance_ledger(con):
    """
    Synthetic Finance ledger: computes the same ARR a naive Stripe-only
    view would show, then applies a small, deliberate variance (Finance
    includes a manual adjustment the Stripe pipeline doesn't see yet,
    e.g. a contract amendment booked directly in the GL) so the
    reconciliation control has real signal to catch, not just a
    trivially-matching mirror.
    """
    # Compute running ARR straight from the already-loaded raw tables in
    # SQL, independent of any dbt model, with explicit casts since
    # load_csv_to_table loads every column as VARCHAR.
    con.execute("CREATE SCHEMA IF NOT EXISTS raw_finance")
    con.execute("SELECT setseed(0.42)")  # deterministic noise across reruns
    con.execute("""
        CREATE OR REPLACE TABLE raw_finance.monthly_revenue_ledger AS
        WITH plans AS (
            SELECT * FROM (VALUES
                ('price_free', 0.0), ('price_starter_m', 9.0), ('price_starter_y', 7.5),
                ('price_pro_m', 29.0), ('price_pro_y', 24.17), ('price_business_m', 99.0),
                ('price_business_y', 82.5), ('price_enterprise_m', 299.0)
            ) AS t(plan_id, monthly_mrr)
        ),
        new_ev AS (
            SELECT customer_id, date_trunc('month', CAST(start_date AS DATE)) AS m, p.monthly_mrr AS delta
            FROM raw_stripe.subscriptions s JOIN plans p ON s.plan_id = p.plan_id
            WHERE s.status = 'active'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY s.customer_id ORDER BY CAST(s.start_date AS DATE)) = 1
        ),
        churn_ev AS (
            SELECT customer_id, date_trunc('month', CAST(canceled_at AS DATE)) AS m, -1 * p.monthly_mrr AS delta
            FROM raw_stripe.subscriptions s JOIN plans p ON s.plan_id = p.plan_id
            WHERE s.status = 'canceled'
        ),
        change_ev AS (
            SELECT customer_id, date_trunc('month', CAST(change_date AS DATE)) AS m,
                   CAST(new_mrr AS DOUBLE) - CAST(old_mrr AS DOUBLE) AS delta
            FROM raw_stripe.plan_changes
        ),
        all_ev AS (
            SELECT * FROM new_ev UNION ALL SELECT * FROM churn_ev UNION ALL SELECT * FROM change_ev
        ),
        monthly_net AS (
            SELECT m AS ledger_month, SUM(delta) AS net_mrr_delta FROM all_ev GROUP BY 1
        ),
        running AS (
            SELECT ledger_month, SUM(net_mrr_delta) OVER (ORDER BY ledger_month) AS mrr_usd FROM monthly_net
        )
        SELECT
            ledger_month,
            -- Finance's recorded ARR = Stripe-derived ARR plus routine
            -- small noise (rounding, timing of GL posting) most months,
            -- plus a larger one-time manual adjustment in two specific
            -- months (a booked contract amendment Finance recorded
            -- directly in the GL that hadn't yet synced through Stripe),
            -- a realistic mixed PASS/FAIL result rather than either a
            -- suspiciously perfect match or noise so wide every month fails
            ROUND(
                mrr_usd * 12 * (1 + (random() * 0.024 - 0.012))
                + CASE
                    WHEN ledger_month IN (DATE '2025-07-01', DATE '2026-03-01')
                        THEN mrr_usd * 12 * 0.032
                    ELSE 0
                  END,
                2
            ) AS recorded_arr_usd
        FROM running
        ORDER BY ledger_month
    """)


def main():
    con = duckdb.connect(DB_PATH)

    tables = ["customers", "subscriptions", "plan_changes", "invoices", "charges", "refunds"]
    for t in tables:
        load_csv_to_table(con, "raw_stripe", t, f"{DATA_DIR}/stripe_{t}.csv")
        count = con.execute(f"select count(*) from raw_stripe.{t}").fetchone()[0]
        print(f"raw_stripe.{t}: {count} rows")

    build_finance_ledger(con)
    ledger_count = con.execute("select count(*) from raw_finance.monthly_revenue_ledger").fetchone()[0]
    print(f"raw_finance.monthly_revenue_ledger: {ledger_count} rows")

    con.close()
    print(f"\nDuckDB database ready at {DB_PATH}")


if __name__ == "__main__":
    main()
