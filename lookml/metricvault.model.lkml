connection: "snowflake_analytics"

# Migration-period artifact: LookML remains the system existing Looker
# dashboards query while consumers migrate onto the MetricFlow-backed
# Tableau extracts. Metric definitions here are wired to read from the
# exact same certified mart tables as semantic_layer/metrics.yml, not
# redefined independently, so the two layers cannot drift apart during
# the transition. Once migration completes, this file is retired.

include: "/views/mrr_movements.view.lkml"
include: "/views/subscription_revenue.view.lkml"

explore: mrr_movements {
  label: "MRR Movements (Legacy Looker)"
  description: "Mirrors the certified MetricFlow mrr_movements semantic model. Same source table, same metric logic."
}

explore: subscription_revenue {
  label: "Subscription Revenue (Legacy Looker)"
  description: "Mirrors the certified MetricFlow subscription_revenue semantic model."
}
