view: subscription_revenue {
  sql_table_name: mart.fct_subscription_revenue ;;

  dimension: customer_id {
    type: string
    sql: ${TABLE}.customer_id ;;
  }

  dimension_group: snapshot {
    type: time
    timeframes: [month, quarter, year]
    sql: ${TABLE}.snapshot_month ;;
  }

  dimension: is_active {
    type: yesno
    sql: ${TABLE}.is_active ;;
  }

  dimension: mrr_usd {
    type: number
    sql: ${TABLE}.mrr_usd ;;
    hidden: yes
  }

  measure: mrr {
    type: sum
    sql: ${mrr_usd} ;;
    label: "MRR"
    description: "CERTIFIED. Mirrors MetricFlow metric: mrr."
    value_format_name: usd
  }

  measure: arr {
    type: number
    sql: ${mrr} * 12 ;;
    label: "ARR"
    description: "CERTIFIED. Mirrors MetricFlow metric: arr. Derived as MRR x 12, never independently defined."
    value_format_name: usd
  }

  measure: paying_customer_count {
    type: count_distinct
    sql: ${customer_id} ;;
    filters: [is_active: "yes"]
    label: "Paying Customers"
    description: "CERTIFIED. Mirrors MetricFlow metric: paying_customer_count."
  }
}
