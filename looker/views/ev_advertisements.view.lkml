view: ev_advertisements {
  sql_table_name: `your_project.your_dataset.ev_ads_data` ;;
  
  # Primary Key
  dimension: ad_archive_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.ad_archive_id ;;
    label: "Ad Archive ID"
  }
  
  # Advertisement Details
  dimension: ad_title {
    type: string
    sql: ${TABLE}.ad_title ;;
    label: "Ad Title"
  }
  
  dimension: ad_description {
    type: string
    sql: ${TABLE}.ad_description ;;
    label: "Ad Description"
  }
  
  # Advertiser Information
  dimension: page_name {
    type: string
    sql: ${TABLE}.page_name ;;
    label: "Advertiser"
    drill_fields: [ad_title, vehicle_model, country]
  }
  
  dimension: advertiser_domain {
    type: string
    sql: ${TABLE}.advertiser_domain ;;
    label: "Advertiser Domain"
  }
  
  # Vehicle Information
  dimension: matched_cars {
    type: string
    sql: ${TABLE}.matched_cars ;;
    label: "Vehicle Model"
    drill_fields: [page_name, country, start_date]
  }
  
  dimension: vehicle_model {
    type: string
    sql: COALESCE(${TABLE}.matched_cars, ${TABLE}.vehicle_model) ;;
    label: "Vehicle Model (Clean)"
  }
  
  # Geographic Information
  dimension: country {
    type: string
    sql: ${TABLE}.country ;;
    label: "Country"
    map_layer_name: world_countries
    drill_fields: [vehicle_model, page_name, start_date]
  }
  
  dimension: region_info {
    type: string
    sql: ${TABLE}.region_info ;;
    label: "Region Info"
  }
  
  # Platform Information
  dimension: source_platform {
    type: string
    sql: ${TABLE}.source_platform ;;
    label: "Platform"
  }
  
  dimension: platform_type {
    type: string
    sql: ${TABLE}.platform_type ;;
    label: "Platform Type"
  }
  
  # Date Dimensions
  dimension_group: start {
    type: time
    timeframes: [raw, date, week, month, quarter, year]
    sql: ${TABLE}.start_date ;;
    label: "Start"
  }
  
  dimension_group: end {
    type: time
    timeframes: [raw, date, week, month, quarter, year]
    sql: ${TABLE}.end_date ;;
    label: "End"
  }
  
  # Performance Metrics
  dimension: impressions_lower {
    type: number
    sql: ${TABLE}.impressions_lower ;;
    label: "Impressions (Lower Bound)"
  }
  
  dimension: impressions_upper {
    type: number
    sql: ${TABLE}.impressions_upper ;;
    label: "Impressions (Upper Bound)"
  }
  
  dimension: reach_estimate {
    type: number
    sql: ${TABLE}.reach_estimate ;;
    label: "Reach Estimate"
  }
  
  dimension: spend {
    type: number
    sql: ${TABLE}.spend ;;
    label: "Spend"
    value_format_name: usd
  }
  
  dimension: page_like_count {
    type: number
    sql: ${TABLE}.page_like_count ;;
    label: "Page Likes"
  }
  
  # OpenAI Analysis
  dimension: openai_analysis {
    type: string
    sql: ${TABLE}.openai_analysis ;;
    label: "AI Analysis"
    html: <div style="max-height: 200px; overflow-y: auto;">{{ value }}</div> ;;
  }
  
  # Creative Information
  dimension: creative_id {
    type: string
    sql: ${TABLE}.creative_id ;;
    label: "Creative ID"
  }
  
  dimension: image_url {
    type: string
    sql: ${TABLE}.image_url ;;
    label: "Image URL"
    html: <img src="{{ value }}" width="200" height="150"> ;;
  }
  
  dimension: cta_text {
    type: string
    sql: ${TABLE}.cta_text ;;
    label: "Call to Action"
  }
  
  # Calculated Dimensions
  dimension: impressions_midpoint {
    type: number
    sql: (${impressions_lower} + ${impressions_upper}) / 2 ;;
    label: "Impressions (Midpoint)"
    value_format_name: decimal_0
  }
  
  dimension: campaign_duration_days {
    type: number
    sql: DATE_DIFF(${end_date}, ${start_date}, DAY) ;;
    label: "Campaign Duration (Days)"
  }
  
  dimension: target_market {
    type: yesno
    sql: ${country} IN ('Portugal', 'Germany', 'Netherlands') ;;
    label: "Target Market"
  }
  
  dimension: target_vehicle {
    type: yesno
    sql: ${vehicle_model} IN ('Hyundai Ioniq 5', 'VW ID.4', 'Renault Megane E-Tech', 'Audi Q4 e-tron', 'Tesla Model Y') ;;
    label: "Target Vehicle"
  }
  
  # Measures
  measure: count {
    type: count
    label: "Total Ads"
    drill_fields: [ad_archive_id, ad_title, page_name, vehicle_model, country]
  }
  
  measure: unique_advertisers {
    type: count_distinct
    sql: ${page_name} ;;
    label: "Unique Advertisers"
  }
  
  measure: unique_vehicles {
    type: count_distinct
    sql: ${vehicle_model} ;;
    label: "Unique Vehicles"
  }
  
  measure: total_spend {
    type: sum
    sql: ${spend} ;;
    label: "Total Spend"
    value_format_name: usd
  }
  
  measure: avg_spend {
    type: average
    sql: ${spend} ;;
    label: "Average Spend"
    value_format_name: usd
  }
  
  measure: total_reach {
    type: sum
    sql: ${reach_estimate} ;;
    label: "Total Reach"
    value_format_name: decimal_0
  }
  
  measure: avg_impressions {
    type: average
    sql: ${impressions_midpoint} ;;
    label: "Average Impressions"
    value_format_name: decimal_0
  }
  
  measure: avg_campaign_duration {
    type: average
    sql: ${campaign_duration_days} ;;
    label: "Average Campaign Duration"
    value_format_name: decimal_1
  }
  
  # Filtered Measures
  measure: target_market_ads {
    type: count
    filters: [target_market: "yes"]
    label: "Target Market Ads"
  }
  
  measure: target_vehicle_ads {
    type: count
    filters: [target_vehicle: "yes"]
    label: "Target Vehicle Ads"
  }
}
