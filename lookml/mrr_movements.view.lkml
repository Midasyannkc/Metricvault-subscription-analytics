view: mrr_movements {
  sql_table_name: mart.fct_mrr_movements ;;

  dimension: movement_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.movement_id ;;
  }

  dimension: customer_id {
    type: string
    sql: ${TABLE}.customer_id ;;
  }

  dimension: movement_type {
    type: string
    sql: ${TABLE}.movement_type ;;
  }

  dimension_group: movement {
    type: time
    timeframes: [month, quarter, year]
    sql: ${TABLE}.movement_month ;;
  }

  dimension: mrr_delta {
    type: number
    sql: ${TABLE}.mrr_delta ;;
    hidden: yes
  }

  # ---- measures, wired to match semantic_layer/metrics.yml exactly ----

  measure: new_mrr {
    type: sum
    sql: ${mrr_delta} ;;
    filters: [movement_type: "new"]
    label: "New MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: new_mrr."
    value_format_name: usd
  }

  measure: expansion_mrr {
    type: sum
    sql: ${mrr_delta} ;;
    filters: [movement_type: "expansion"]
    label: "Expansion MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: expansion_mrr."
    value_format_name: usd
  }

  measure: contraction_mrr {
    type: sum
    sql: ${mrr_delta} ;;
    filters: [movement_type: "contraction"]
    label: "Contraction MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: contraction_mrr."
    value_format_name: usd
  }

  measure: churned_mrr {
    type: sum
    sql: ${mrr_delta} ;;
    filters: [movement_type: "churned"]
    label: "Churned MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: churned_mrr."
    value_format_name: usd
  }

  measure: net_new_mrr {
    type: sum
    sql: ${mrr_delta} ;;
    label: "Net New MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: net_new_mrr. Sum of all movement types for the period."
    value_format_name: usd
  }
}
