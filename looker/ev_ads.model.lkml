# EV Advertisement Analysis Model
connection: "your_database_connection"

include: "/views/*.view.lkml"

datagroup: ev_ads_default_datagroup {
  sql_trigger: SELECT MAX(id) FROM ${ev_advertisements.SQL_TABLE_NAME};;
  max_cache_age: "1 hour"
}

persist_with: ev_ads_default_datagroup

explore: ev_advertisements {
  label: "EV Advertisement Analysis"
  description: "Analysis of electric vehicle advertisements across European markets"
  
  join: openai_features {
    type: left_outer
    sql_on: ${ev_advertisements.ad_archive_id} = ${openai_features.ad_archive_id} ;;
    relationship: one_to_many
  }
  
  join: market_mapping {
    type: left_outer
    sql_on: ${ev_advertisements.country} = ${market_mapping.country_code} ;;
    relationship: many_to_one
  }
}
