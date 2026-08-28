# Change Management Control

Maps to SOX ITGC change-management objectives: no change to a
financial-reporting-relevant metric definition reaches production
without independent review, and every change is traceable to who
approved it and why.

## Control design

Every model in `dbt/models/marts/` that backs a certified metric
(`fct_mrr_movements`, `fct_subscription_revenue`, `fct_finance_reconciliation`)
is tagged in `_marts__schema.yml`. Any pull request touching a tagged
model triggers this required workflow:

1. **Author opens a PR.** The PR description must state which certified
   metric(s) are affected and why the change is needed.
2. **CI runs automatically**: `dbt build` (all models + tests) against
   a CI-isolated warehouse clone, plus `dbt docs generate` to confirm
   the lineage graph still resolves. A failing test blocks merge.
3. **Independent review required.** At least one reviewer who is not
   the PR author must approve, and for changes to `fct_finance_reconciliation`
   specifically, a Finance stakeholder is a required reviewer (not just
   Analytics Engineering), since that model's correctness is what the
   reconciliation control depends on.
4. **Merge triggers the production `dbt build`** under the CI service
   account, never a human's personal Snowflake credentials.
5. **The exposure metadata in `_marts__schema.yml`** (owner, dashboard
   URL, `depends_on`) is required to stay current with every merge, so
   "who owns this number and what reads it" is always answerable from
   the repo itself, not from institutional memory.

## Why this matters for this specific project

`fct_finance_reconciliation` is the model that would actually get
audited in a SOX walkthrough: it's the evidence that the data team's
ARR number and Finance's independently-recorded number are checked
against each other every month, and that a variance beyond threshold
is visible (not silently absorbed). The change-management control
above exists specifically so nobody can quietly loosen the 2% threshold
or change the underlying ARR calculation without a Finance stakeholder
signing off, that's the control an auditor is actually testing for.

## What this repo demonstrates vs. what's out of scope

This repo demonstrates the review requirement and CI gate as documented
process (this file) plus the actual passing CI run (`dbt build`,
verified in `docs/dagster_run_log.txt`). A live GitHub branch-protection
rule enforcing "1 approval required, Finance required for marts/
changes" is a repository setting, not code, and isn't simulable inside
this project, it's noted here as the production configuration this
control design assumes.
