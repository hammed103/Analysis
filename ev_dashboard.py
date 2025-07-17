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
    csv_files = [
        "work.csv",
        "Data/merged_ev_ads_dataset_20250716_171722.csv",
        "Data/merged_ev_ads_dataset_20250716_170109.csv",
    ]

    for file_path in csv_files:
        if os.path.exists(file_path):
            return EVAdvertAnalyzer(file_path)

    st.error("No data file found. Please ensure one of the expected CSV files exists.")
    st.stop()


def main():
    """Main dashboard function"""

    # Header
    st.title("🚗 EV Advertisement Analysis Dashboard")
    st.markdown("**Competitor Analysis for Electric Vehicle Advertisements**")
    st.markdown("*Analyzing Portugal, Germany, and Netherlands markets*")

    # Load data
    with st.spinner("Loading data..."):
        analyzer = load_data()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Market filter
    markets = ["All"] + ["Portugal", "Germany", "Netherlands"]
    selected_market = st.sidebar.selectbox("Select Market", markets)

    # Vehicle filter
    vehicles = ["All"] + list(analyzer.df_filtered["vehicle_model"].unique())
    selected_vehicle = st.sidebar.selectbox("Select Vehicle", vehicles)

    # Create tabs for different analysis views
    tab1, tab2 = st.tabs(["📊 Overview", "🔍 Feature Analysis"])

    with tab1:
        # Main content
        col1, col2, col3, col4 = st.columns(4)

    # Key metrics
    total_ads = len(analyzer.df_filtered)
    unique_vehicles = analyzer.df_filtered["vehicle_model"].nunique()
    unique_advertisers = (
        analyzer.df_filtered["page_name"].nunique()
        if "page_name" in analyzer.df_filtered.columns
        else 0
    )
    start_date = analyzer.df_filtered["start_date"].min().strftime("%Y-%m")
    end_date = analyzer.df_filtered["start_date"].max().strftime("%Y-%m")
    date_range = f"{start_date} to {end_date}"

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
        # Market distribution
        market_summary = analyzer.get_market_summary()
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
        # Vehicle distribution
        vehicle_analysis = analyzer.get_vehicle_analysis()
        vehicle_data = []
        for vehicle, stats in vehicle_analysis.items():
            vehicle_data.append({"Vehicle": vehicle, "Total Ads": stats["total_ads"]})

        if vehicle_data:
            vehicle_df = pd.DataFrame(vehicle_data).sort_values(
                "Total Ads", ascending=False
            )
            fig_vehicle = px.pie(
                vehicle_df,
                values="Total Ads",
                names="Vehicle",
                title="Advertisement Share by Vehicle Model",
            )
            st.plotly_chart(
                fig_vehicle, use_container_width=True, key="vehicle_pie_chart"
            )

    # Feature Analysis
    st.header("🔧 Feature Analysis")

    feature_analysis = analyzer.analyze_features_mentioned()

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
                        index="Feature", columns="Vehicle", values="Count", fill_value=0
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
                        fig_heatmap, use_container_width=True, key="features_heatmap"
                    )
                else:
                    # Show feature details for selected vehicle
                    if selected_vehicle in feature_analysis:
                        vehicle_features = feature_analysis[selected_vehicle]
                        st.subheader(f"Feature Details: {selected_vehicle}")

                        for feature, count in sorted(
                            vehicle_features.items(), key=lambda x: x[1], reverse=True
                        ):
                            st.write(f"**{feature}**: {count} mentions")

        # Market vs Vehicle Analysis
        st.header("🌍 Market vs Vehicle Analysis")

        # Create market-vehicle matrix
        market_vehicle_data = []
        vehicle_analysis = analyzer.get_vehicle_analysis()

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

        if "start_date" in analyzer.df_filtered.columns:
            # Prepare time series data
            df_time = analyzer.df_filtered.copy()
            df_time["start_date"] = pd.to_datetime(df_time["start_date"])
            df_time["year_month"] = df_time["start_date"].dt.to_period("M")

            # Filter by selected market and vehicle
            if selected_market != "All":
                if "country" in df_time.columns:
                    df_time = df_time[df_time["country"] == selected_market]

            if selected_vehicle != "All":
                df_time = df_time[df_time["vehicle_model"] == selected_vehicle]

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
                        selected_market if selected_market != "All" else "All Markets"
                    )
                    vehicle_text = (
                        selected_vehicle
                        if selected_vehicle != "All"
                        else "All Vehicles"
                    )
                    title = f"Advertisement Volume Over Time ({market_text} - {vehicle_text})"

                fig_time = px.line(
                    time_series, x="year_month", y="ad_count", title=title, markers=True
                )
                fig_time.update_xaxes(tickangle=45)
                st.plotly_chart(
                    fig_time, use_container_width=True, key="time_series_chart"
                )

    # Market vs Vehicle Analysis
    st.header("🌍 Market vs Vehicle Analysis")

    # Create market-vehicle matrix
    market_vehicle_data = []
    vehicle_analysis = analyzer.get_vehicle_analysis()

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
        st.plotly_chart(fig_mv, use_container_width=True)

    # Time Series Analysis
    st.header("📈 Time Series Analysis")

    if "start_date" in analyzer.df_filtered.columns:
        # Prepare time series data
        df_time = analyzer.df_filtered.copy()
        df_time["start_date"] = pd.to_datetime(df_time["start_date"])
        df_time["year_month"] = df_time["start_date"].dt.to_period("M")

        # Filter by selected market and vehicle
        if selected_market != "All":
            if "country" in df_time.columns:
                df_time = df_time[df_time["country"] == selected_market]

        if selected_vehicle != "All":
            df_time = df_time[df_time["vehicle_model"] == selected_vehicle]

        # Create time series
        time_series = df_time.groupby("year_month").size().reset_index(name="ad_count")
        time_series["year_month"] = time_series["year_month"].astype(str)

        if len(time_series) > 0:
            # Create title based on filters
            if selected_market == "All" and selected_vehicle == "All":
                title = "Advertisement Volume Over Time (All)"
            else:
                market_text = (
                    selected_market if selected_market != "All" else "All Markets"
                )
                vehicle_text = (
                    selected_vehicle if selected_vehicle != "All" else "All Vehicles"
                )
                title = (
                    f"Advertisement Volume Over Time ({market_text} - {vehicle_text})"
                )

            fig_time = px.line(
                time_series, x="year_month", y="ad_count", title=title, markers=True
            )
            fig_time.update_xaxes(tickangle=45)
            st.plotly_chart(fig_time, use_container_width=True)

    # Data Export
    st.header("💾 Data Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export Market Summary"):
            market_summary = analyzer.get_market_summary()
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
            feature_analysis = analyzer.analyze_features_mentioned()
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

        # Get feature analysis data
        feature_analysis = analyzer.analyze_features_mentioned()

        if not feature_analysis:
            st.warning("No feature analysis data available.")
            return

        # Vehicle selection for feature analysis
        st.subheader("Select Vehicle for Feature Analysis")
        feature_vehicles = ["All"] + list(feature_analysis.keys())
        selected_feature_vehicle = st.selectbox(
            "Choose Vehicle", feature_vehicles, key="feature_vehicle_select"
        )

        # Filter feature analysis based on selection
        if selected_feature_vehicle == "All":
            display_features = feature_analysis
        else:
            display_features = {
                selected_feature_vehicle: feature_analysis[selected_feature_vehicle]
            }

        # Display feature analysis for each vehicle
        for vehicle, features in display_features.items():
            st.subheader(f"Feature Details: {vehicle}")

            # Sort features by mention count
            sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)

            # Create expandable sections for each feature
            for feature_name, mention_count in sorted_features:
                with st.expander(f"**{feature_name}**: {mention_count} mentions"):
                    # Get detailed mentions for this specific feature and vehicle
                    detailed_mentions = analyzer.get_feature_mentions_detail(
                        feature_category=feature_name,
                        vehicle_model=vehicle if vehicle != "All" else None,
                    )

                    if detailed_mentions:
                        # Filter out "Not specified" mentions and other low-quality content
                        filtered_mentions = []
                        seen_content = set()  # Track unique content

                        for mention in detailed_mentions:
                            content = mention.get("relevant_text", "").lower().strip()

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
