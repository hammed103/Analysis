#!/usr/bin/env python3
"""
EV Advertisement Analysis Dashboard
Streamlit dashboard for analyzing electric vehicle advertisements
across Portugal, Germany, and Netherlands
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import EVAdvertAnalyzer
import os

# Page configuration
st.set_page_config(
    page_title="EV Advertisement Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """Load and cache the data"""
    # Priority order for data sources
    data_sources = [
        "Data",  # Split data directory (preferred for GitHub deployment)
        "work.csv",  # Single file (local development)
        "Data/merged_ev_ads_dataset_20250716_171722.csv",
        "Data/merged_ev_ads_dataset_20250716_170109.csv",
        "sample_data.csv",  # Demo data (lowest priority)
    ]

    for data_source in data_sources:
        if os.path.exists(data_source):
            try:
                analyzer = EVAdvertAnalyzer(data_source)
                if os.path.isdir(data_source):
                    st.success(f"✅ Loaded data from {data_source}/ directory")
                else:
                    st.success(f"✅ Loaded data from {data_source}")
                return analyzer
            except Exception as e:
                st.warning(f"⚠️ Failed to load {data_source}: {e}")
                continue

    st.error(
        "❌ No valid data source found. Please ensure one of these exists:\n"
        "- `data/` directory with split CSV files\n"
        "- `work.csv` file\n"
        "- `sample_data.csv` file"
    )
    st.stop()


@st.cache_data
def get_cached_analysis_data(_analyzer):
    """Cache expensive analysis operations"""
    return {
        "market_summary": _analyzer.get_market_summary(),
        "vehicle_analysis": _analyzer.get_vehicle_analysis(),
        "feature_analysis": _analyzer.analyze_features_mentioned(),
    }


@st.cache_data
def filter_dataframe(df, selected_market, selected_vehicle):
    """Cache filtered dataframe operations"""
    filtered_df = df.copy()

    # Apply market filter
    if selected_market != "All":
        if "country" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["country"] == selected_market]

    # Apply vehicle filter
    if selected_vehicle != "All":
        filtered_df = filtered_df[filtered_df["vehicle_model"] == selected_vehicle]

    return filtered_df


@st.cache_data
def get_feature_mentions_detail(_analyzer, feature_category, vehicle_model=None):
    """Cache feature mentions detail to improve performance"""
    return _analyzer.get_feature_mentions_detail(
        feature_category=feature_category, vehicle_model=vehicle_model
    )


@st.cache_data
def get_filtered_market_summary(df, selected_market):
    """Get market summary for filtered data"""
    summary = {}

    markets_to_show = ["Portugal", "Germany", "Netherlands"]
    if selected_market != "All":
        markets_to_show = [selected_market]

    for market in markets_to_show:
        if "country" in df.columns:
            market_data = df[df["country"] == market]

            if len(market_data) > 0:
                summary[market] = {
                    "total_ads": len(market_data),
                    "unique_vehicles": market_data["vehicle_model"].nunique(),
                    "unique_advertisers": (
                        market_data["page_name"].nunique()
                        if "page_name" in market_data.columns
                        else 0
                    ),
                    "date_range": {
                        "start": (
                            market_data["start_date"].min().strftime("%Y-%m")
                            if pd.notna(market_data["start_date"].min())
                            else "N/A"
                        ),
                        "end": (
                            market_data["start_date"].max().strftime("%Y-%m")
                            if pd.notna(market_data["start_date"].max())
                            else "N/A"
                        ),
                    },
                }

    return summary


@st.cache_data
def get_filtered_vehicle_analysis(df, selected_market, selected_vehicle):
    """Get vehicle analysis for filtered data"""
    analysis = {}

    # Apply market filter if specified
    filtered_df = df.copy()
    if selected_market != "All" and "country" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["country"] == selected_market]

    # Get vehicles to analyze
    vehicles_to_analyze = filtered_df["vehicle_model"].unique()
    if selected_vehicle != "All":
        vehicles_to_analyze = (
            [selected_vehicle] if selected_vehicle in vehicles_to_analyze else []
        )

    for vehicle in vehicles_to_analyze:
        vehicle_data = filtered_df[filtered_df["vehicle_model"] == vehicle]

        if len(vehicle_data) > 0:
            # Get market breakdown for this vehicle
            market_breakdown = {}
            if "country" in vehicle_data.columns:
                for market in ["Portugal", "Germany", "Netherlands"]:
                    market_ads = vehicle_data[vehicle_data["country"] == market]
                    if len(market_ads) > 0:
                        market_breakdown[market] = len(market_ads)

            analysis[vehicle] = {
                "total_ads": len(vehicle_data),
                "unique_advertisers": (
                    vehicle_data["page_name"].nunique()
                    if "page_name" in vehicle_data.columns
                    else 0
                ),
                "market_breakdown": market_breakdown,
                "date_range": {
                    "start": (
                        vehicle_data["start_date"].min().strftime("%Y-%m")
                        if pd.notna(vehicle_data["start_date"].min())
                        else "N/A"
                    ),
                    "end": (
                        vehicle_data["start_date"].max().strftime("%Y-%m")
                        if pd.notna(vehicle_data["start_date"].max())
                        else "N/A"
                    ),
                },
            }

    return analysis


def main():
    """Main dashboard function"""

    # Header
    st.title("🚗 EV Advertisement Analysis Dashboard")
    st.markdown("**Competitor Analysis for Electric Vehicle Advertisements**")
    st.markdown("*Analyzing Portugal, Germany, and Netherlands markets*")

    # Load data
    with st.spinner("Loading data..."):
        analyzer = load_data()

    # Cache expensive analysis operations
    with st.spinner("Preparing analysis data..."):
        cached_data = get_cached_analysis_data(analyzer)

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Market filter
    markets = ["All"] + ["Portugal", "Germany", "Netherlands"]
    selected_market = st.sidebar.selectbox(
        "Select Market", markets, key="market_filter"
    )

    # Vehicle filter - use cached data for better performance
    vehicles = ["All"] + sorted(list(analyzer.df_filtered["vehicle_model"].unique()))
    selected_vehicle = st.sidebar.selectbox(
        "Select Vehicle", vehicles, key="vehicle_filter"
    )

    # Get filtered dataframe using cached function
    filtered_df = filter_dataframe(
        analyzer.df_filtered, selected_market, selected_vehicle
    )

    # Create tabs for different analysis views
    tab1, tab2 = st.tabs(["📊 Overview", "🔍 Feature Analysis"])

    with tab1:
        # Main content
        col1, col2, col3, col4 = st.columns(4)

        # Key metrics based on filtered data
        total_ads = len(filtered_df)
        unique_vehicles = filtered_df["vehicle_model"].nunique()
        unique_advertisers = (
            filtered_df["page_name"].nunique()
            if "page_name" in filtered_df.columns
            else 0
        )

        if len(filtered_df) > 0 and "start_date" in filtered_df.columns:
            try:
                start_date_val = filtered_df["start_date"].min()
                end_date_val = filtered_df["start_date"].max()

                # Check if dates are not NaT (Not a Time)
                if pd.notna(start_date_val) and pd.notna(end_date_val):
                    start_date = start_date_val.strftime("%Y-%m")
                    end_date = end_date_val.strftime("%Y-%m")
                    date_range = f"{start_date} to {end_date}"
                else:
                    date_range = "Date unavailable"
            except (AttributeError, ValueError):
                date_range = "Date unavailable"
        else:
            date_range = "No data"

        with col1:
            st.metric("Total Ads", f"{total_ads:,}")
        with col2:
            st.metric("Unique Vehicles", unique_vehicles)
        with col3:
            st.metric("Unique Advertisers", unique_advertisers)
        with col4:
            st.metric("Date Range", date_range)

        # Market Overview
        st.header("📊 Market Overview")

        col1, col2 = st.columns(2)

        with col1:
            # Market distribution (use cached data)
            market_summary = cached_data["market_summary"]
            market_data = []
            for market, stats in market_summary.items():
                market_data.append(
                    {
                        "Market": market,
                        "Total Ads": stats["total_ads"],
                        "Unique Vehicles": stats["unique_vehicles"],
                        "Unique Advertisers": stats["unique_advertisers"],
                    }
                )

            if market_data:
                market_df = pd.DataFrame(market_data)
                fig_market = px.bar(
                    market_df,
                    x="Market",
                    y="Total Ads",
                    title="Advertisement Volume by Market",
                    color="Market",
                    color_discrete_map={
                        "Portugal": "#FF6B6B",
                        "Germany": "#4ECDC4",
                        "Netherlands": "#45B7D1",
                    },
                )
                fig_market.update_layout(showlegend=False)
                st.plotly_chart(
                    fig_market, use_container_width=True, key="market_bar_chart"
                )

        with col2:
            # Vehicle distribution (show filtered data)
            if len(filtered_df) > 0:
                vehicle_counts = filtered_df["vehicle_model"].value_counts()
                vehicle_data = []
                for vehicle, count in vehicle_counts.items():
                    vehicle_data.append({"Vehicle": vehicle, "Total Ads": count})

                if vehicle_data:
                    vehicle_df = pd.DataFrame(vehicle_data).sort_values(
                        "Total Ads", ascending=False
                    )
                    title_suffix = ""
                    if selected_market != "All" or selected_vehicle != "All":
                        filters = []
                        if selected_market != "All":
                            filters.append(selected_market)
                        if selected_vehicle != "All":
                            filters.append(selected_vehicle)
                        title_suffix = f" ({', '.join(filters)})"

                    fig_vehicle = px.pie(
                        vehicle_df,
                        values="Total Ads",
                        names="Vehicle",
                        title=f"Advertisement Share by Vehicle Model{title_suffix}",
                    )
                    st.plotly_chart(
                        fig_vehicle, use_container_width=True, key="vehicle_pie_chart"
                    )
            else:
                st.warning("No data available for the selected filters.")

        # Feature Analysis
        st.header("🔧 Feature Analysis")

        feature_analysis = cached_data["feature_analysis"]

        if feature_analysis:
            # Create feature comparison chart
            feature_data = []
            for vehicle, features in feature_analysis.items():
                for feature, count in features.items():
                    feature_data.append(
                        {"Vehicle": vehicle, "Feature": feature, "Count": count}
                    )

            if feature_data:
                feature_df = pd.DataFrame(feature_data)

                # Filter by selected vehicle if not "All"
                if selected_vehicle != "All":
                    feature_df = feature_df[feature_df["Vehicle"] == selected_vehicle]

                # Top features overall
                top_features = (
                    feature_df.groupby("Feature")["Count"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                )

                col1, col2 = st.columns(2)

                with col1:
                    # Feature frequency chart
                    # Create title
                    title_suffix = (
                        "(All Vehicles)"
                        if selected_vehicle == "All"
                        else f"({selected_vehicle})"
                    )
                    title = f"Top Features Mentioned {title_suffix}"

                    fig_features = px.bar(
                        x=top_features.values,
                        y=top_features.index,
                        orientation="h",
                        title=title,
                        labels={"x": "Mentions", "y": "Feature Category"},
                    )
                    fig_features.update_layout(height=400)
                    st.plotly_chart(
                        fig_features, use_container_width=True, key="features_bar_chart"
                    )

                with col2:
                    # Feature comparison by vehicle (if All selected)
                    if selected_vehicle == "All" and len(feature_analysis) > 1:
                        # Create heatmap of features by vehicle
                        pivot_df = feature_df.pivot_table(
                            index="Feature",
                            columns="Vehicle",
                            values="Count",
                            fill_value=0,
                        )

                        fig_heatmap = px.imshow(
                            pivot_df.values,
                            x=pivot_df.columns,
                            y=pivot_df.index,
                            title="Feature Mentions Heatmap",
                            color_continuous_scale="Blues",
                        )
                        fig_heatmap.update_layout(height=400)
                        st.plotly_chart(
                            fig_heatmap,
                            use_container_width=True,
                            key="features_heatmap",
                        )
                    else:
                        # Show feature details for selected vehicle
                        if selected_vehicle in feature_analysis:
                            vehicle_features = feature_analysis[selected_vehicle]
                            st.subheader(f"Feature Details: {selected_vehicle}")

                            for feature, count in sorted(
                                vehicle_features.items(),
                                key=lambda x: x[1],
                                reverse=True,
                            ):
                                st.write(f"**{feature}**: {count} mentions")

        # Market vs Vehicle Analysis
        st.header("🌍 Market vs Vehicle Analysis")

        # Create market-vehicle matrix using cached data
        market_vehicle_data = []
        vehicle_analysis = cached_data["vehicle_analysis"]

        for vehicle, stats in vehicle_analysis.items():
            for market, count in stats["market_breakdown"].items():
                # Normalize market names
                normalized_market = market
                if market in ["PT"]:
                    normalized_market = "Portugal"
                elif market in ["DE"]:
                    normalized_market = "Germany"
                elif market in ["NL"]:
                    normalized_market = "Netherlands"

                market_vehicle_data.append(
                    {"Vehicle": vehicle, "Market": normalized_market, "Ad_Count": count}
                )

        if market_vehicle_data:
            mv_df = pd.DataFrame(market_vehicle_data)
            # Group by normalized market names
            mv_df = mv_df.groupby(["Vehicle", "Market"])["Ad_Count"].sum().reset_index()

            # Create stacked bar chart
            fig_mv = px.bar(
                mv_df,
                x="Vehicle",
                y="Ad_Count",
                color="Market",
                title="Advertisement Volume by Vehicle and Market",
                color_discrete_map={
                    "Portugal": "#FF6B6B",
                    "Germany": "#4ECDC4",
                    "Netherlands": "#45B7D1",
                },
            )
            fig_mv.update_layout(height=500)
            st.plotly_chart(
                fig_mv, use_container_width=True, key="market_vehicle_chart"
            )

        # Time Series Analysis
        st.header("📈 Time Series Analysis")

        if "start_date" in filtered_df.columns and len(filtered_df) > 0:
            # Use filtered data for time series
            df_time = filtered_df.copy()
            df_time["start_date"] = pd.to_datetime(
                df_time["start_date"], errors="coerce"
            )

            # Remove rows with NaT dates
            df_time = df_time.dropna(subset=["start_date"])

            if len(df_time) > 0:
                df_time["year_month"] = df_time["start_date"].dt.to_period("M")

                # Create time series
                time_series = (
                    df_time.groupby("year_month").size().reset_index(name="ad_count")
                )
                time_series["year_month"] = time_series["year_month"].astype(str)

                if len(time_series) > 0:
                    # Create title based on filters
                    if selected_market == "All" and selected_vehicle == "All":
                        title = "Advertisement Volume Over Time (All)"
                    else:
                        market_text = (
                            selected_market
                            if selected_market != "All"
                            else "All Markets"
                        )
                        vehicle_text = (
                            selected_vehicle
                            if selected_vehicle != "All"
                            else "All Vehicles"
                        )
                        title = f"Advertisement Volume Over Time ({market_text} - {vehicle_text})"

                    fig_time = px.line(
                        time_series,
                        x="year_month",
                        y="ad_count",
                        title=title,
                        markers=True,
                    )
                    fig_time.update_xaxes(tickangle=45)
                    st.plotly_chart(
                        fig_time, use_container_width=True, key="time_series_chart"
                    )
                else:
                    st.warning(
                        "No time series data available for the selected filters."
                    )
            else:
                st.warning("No valid date data available for time series analysis.")
        else:
            st.warning("No time series data available for the selected filters.")

        # Data Export
        st.header("💾 Data Export")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Export Market Summary"):
                market_summary = cached_data["market_summary"]
                market_export_df = pd.DataFrame(
                    [
                        {
                            "Market": market,
                            "Total_Ads": stats["total_ads"],
                            "Unique_Vehicles": stats["unique_vehicles"],
                            "Unique_Advertisers": stats["unique_advertisers"],
                            "Date_Start": stats["date_range"]["start"],
                            "Date_End": stats["date_range"]["end"],
                        }
                        for market, stats in market_summary.items()
                    ]
                )

                csv = market_export_df.to_csv(index=False)
                st.download_button(
                    label="Download Market Summary CSV",
                    data=csv,
                    file_name="market_summary.csv",
                    mime="text/csv",
                )

        with col2:
            if st.button("Export Feature Analysis"):
                feature_analysis = cached_data["feature_analysis"]
                feature_export_data = []

                for vehicle, features in feature_analysis.items():
                    for feature, count in features.items():
                        feature_export_data.append(
                            {
                                "Vehicle": vehicle,
                                "Feature_Category": feature,
                                "Mention_Count": count,
                            }
                        )

                if feature_export_data:
                    feature_export_df = pd.DataFrame(feature_export_data)
                    csv = feature_export_df.to_csv(index=False)
                    st.download_button(
                        label="Download Feature Analysis CSV",
                        data=csv,
                        file_name="feature_analysis.csv",
                        mime="text/csv",
                    )

        with col3:
            if st.button("Export Market-Vehicle Matrix"):
                if market_vehicle_data:
                    mv_export_df = pd.DataFrame(market_vehicle_data)
                    csv = mv_export_df.to_csv(index=False)
                    st.download_button(
                        label="Download Market-Vehicle CSV",
                        data=csv,
                        file_name="market_vehicle_analysis.csv",
                        mime="text/csv",
                    )

    # Feature Analysis Tab
    with tab2:
        st.header("🔍 Detailed Feature Analysis")
        st.markdown("Explore actual mentions for each feature category")

        # Get feature analysis data from cache
        feature_analysis = cached_data["feature_analysis"]

        if not feature_analysis:
            st.warning("No feature analysis data available.")
            return

        # Use the same vehicle selection from sidebar
        if selected_vehicle == "All":
            st.subheader("Feature Analysis for: All Vehicles")
            display_features = feature_analysis
        else:
            st.subheader(f"Feature Analysis for: {selected_vehicle}")
            if selected_vehicle in feature_analysis:
                display_features = {
                    selected_vehicle: feature_analysis[selected_vehicle]
                }
            else:
                st.warning(f"No feature analysis data available for {selected_vehicle}")
                display_features = {}

        # Show filter status
        if selected_vehicle != "All" or selected_market != "All":
            filters_applied = []
            if selected_market != "All":
                filters_applied.append(f"Market: {selected_market}")
            if selected_vehicle != "All":
                filters_applied.append(f"Vehicle: {selected_vehicle}")
            st.info(f"🔍 Filters applied: {', '.join(filters_applied)}")

        # Display feature analysis for each vehicle
        for vehicle, features in display_features.items():
            st.subheader(f"Feature Details: {vehicle}")

            # Sort features by mention count
            sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)

            # Create expandable sections for each feature
            for feature_name, mention_count in sorted_features:
                with st.expander(f"**{feature_name}**: {mention_count} mentions"):
                    # Get detailed mentions for this specific feature and vehicle (cached)
                    detailed_mentions = get_feature_mentions_detail(
                        analyzer,
                        feature_category=feature_name,
                        vehicle_model=(
                            selected_vehicle if selected_vehicle != "All" else None
                        ),
                    )

                    if detailed_mentions:
                        # Filter out "Not specified" mentions and other low-quality content
                        filtered_mentions = []
                        seen_content = set()  # Track unique content

                        for mention in detailed_mentions:
                            content = mention.get("relevant_text", "").lower().strip()
                            section = mention.get("matched_keyword", "").lower().strip()

                            # Skip mentions from dealership/advertiser section
                            if "dealership" in section or "advertiser" in section:
                                continue

                            # Skip mentions that contain "not specified" variations
                            if any(
                                phrase in content
                                for phrase in [
                                    "not specified in the ad",
                                    "not specified",
                                    "not mentioned",
                                    "not provided",
                                    "not available",
                                    "no specific",
                                    "no details",
                                    "not detailed",
                                    "not discussed in the ad",
                                    "not discussed",
                                    "not highlighted",
                                    "not emphasized",
                                    "not featured",
                                    "not shown",
                                    "not visible",
                                    "not clear",
                                    "unclear",
                                    "no information",
                                    "no mention",
                                ]
                            ):
                                continue

                            # Also skip very short content (likely not meaningful)
                            if len(content) < 15:
                                continue

                            # Skip duplicates based on content
                            if content in seen_content:
                                continue

                            seen_content.add(content)
                            filtered_mentions.append(mention)

                        if filtered_mentions:
                            st.write(
                                f"**Total Quality Mentions**: {len(filtered_mentions)} unique mentions "
                                f"(filtered from {len(detailed_mentions)} total)"
                            )

                            # Option to show all mentions
                            checkbox_label = f"Show all {len(filtered_mentions)} mentions (default: first 50)"
                            show_all = st.checkbox(
                                checkbox_label,
                                key=f"show_all_{feature_name}_{vehicle}",
                            )

                            st.write("---")

                            # Determine how many to display
                            if show_all:
                                display_count = len(filtered_mentions)
                                mention_count = len(filtered_mentions)
                                st.info(f"Showing all {mention_count} unique mentions")
                            else:
                                display_count = min(50, len(filtered_mentions))
                                if len(filtered_mentions) > 50:
                                    mention_count = len(filtered_mentions)
                                    st.info(
                                        f"Showing first 50 of {mention_count} unique mentions"
                                    )

                            # Display mentions with full details
                            for i, mention in enumerate(
                                filtered_mentions[:display_count]
                            ):
                                st.write(f"**Mention {i+1}:**")

                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    st.write(f"**Advertiser**: {mention['advertiser']}")
                                    st.write(
                                        f"**Platform**: {mention['source_platform']}"
                                    )
                                    st.write(
                                        f"**Section**: {mention['matched_keyword']}"
                                    )

                                with col2:
                                    st.write(f"**Content**: {mention['relevant_text']}")

                                if i < display_count - 1:
                                    st.write("---")
                        else:
                            st.write(
                                "No quality mentions found after filtering out 'not specified' content."
                            )
                    else:
                        st.write("No detailed mentions found for this feature.")


if __name__ == "__main__":
    main()
