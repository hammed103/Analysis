import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from data_processor import EVAdvertAnalyzer
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="EV Competitor Advert Analysis",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .feature-summary {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_analyzer():
    """Load the data analyzer with caching"""
    try:
        analyzer = EVAdvertAnalyzer("work.csv")
        return analyzer
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def main():
    st.markdown(
        '<h1 class="main-header">🚗 EV Competitor Advert Analysis Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.markdown("**Markets:** Portugal 🇵🇹 | Germany 🇩🇪 | Netherlands 🇳🇱")
    st.markdown(
        "**Target Vehicles:** Hyundai Ioniq 5 | VW ID.4 | Renault Megane E-Tech | Audi Q4 e-tron | Tesla Model Y"
    )

    # Load data
    analyzer = load_analyzer()
    if analyzer is None:
        st.stop()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Market selection (normalized)
    available_markets = ["All", "Portugal", "Germany", "Netherlands"]
    selected_market = st.sidebar.selectbox("Select Market", available_markets)

    # Vehicle selection (only target vehicles)
    target_vehicles = [
        "Hyundai Ioniq 5",
        "VW ID.4",
        "Renault Megane E-Tech",
        "Audi Q4 e-tron",
        "Tesla Model Y",
    ]
    available_vehicles = ["All"] + target_vehicles
    selected_vehicle = st.sidebar.selectbox("Select Vehicle", available_vehicles)

    # Show data info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Data Summary**")
    st.sidebar.markdown(f"**Total Records:** {len(analyzer.df_filtered):,}")
    st.sidebar.markdown(f"**Date Range:** All available data")
    if "start_date" in analyzer.df_filtered.columns:
        min_date = analyzer.df_filtered["start_date"].min()
        max_date = analyzer.df_filtered["start_date"].max()
        if pd.notna(min_date) and pd.notna(max_date):
            st.sidebar.markdown(f"**From:** {min_date.strftime('%Y-%m-%d')}")
            st.sidebar.markdown(f"**To:** {max_date.strftime('%Y-%m-%d')}")

    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "🚗 Vehicle Analysis",
            "🎯 Feature Analysis",
            "🖼️ Image Themes",
            "📝 Meta Analysis",
        ]
    )

    with tab1:
        show_overview(analyzer, selected_market)

    with tab2:
        show_vehicle_analysis(analyzer, selected_market, selected_vehicle)

    with tab3:
        show_feature_analysis(analyzer, selected_market, selected_vehicle)

    with tab4:
        show_image_analysis(analyzer, selected_market, selected_vehicle)

    with tab5:
        show_meta_analysis(analyzer, selected_market, selected_vehicle)


def show_overview(analyzer, selected_market):
    """Display overview statistics"""
    st.header("📊 Market Overview")

    # Get market summary
    market_summary = analyzer.get_market_summary()

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    total_ads = len(analyzer.df_filtered)
    unique_vehicles = analyzer.df_filtered["vehicle_model"].nunique()
    unique_advertisers = analyzer.df_filtered["page_name"].nunique()

    with col1:
        st.metric("Total Advertisements", f"{total_ads:,}")
    with col2:
        st.metric("Unique Vehicles", unique_vehicles)
    with col3:
        st.metric("Unique Advertisers", unique_advertisers)
    with col4:
        markets_covered = len(
            [m for m in market_summary.keys() if market_summary[m]["total_ads"] > 0]
        )
        st.metric("Markets Covered", markets_covered)

    # Market breakdown chart
    st.subheader("📈 Advertisements by Market")

    market_data = []
    for market, data in market_summary.items():
        if data["total_ads"] > 0:
            market_data.append(
                {
                    "Market": market,
                    "Total Ads": data["total_ads"],
                    "Unique Vehicles": data["unique_vehicles"],
                    "Unique Advertisers": data["unique_advertisers"],
                }
            )

    if market_data:
        df_market = pd.DataFrame(market_data)

        col1, col2 = st.columns(2)

        with col1:
            fig_ads = px.bar(
                df_market,
                x="Market",
                y="Total Ads",
                title="Total Advertisements by Market",
                color="Total Ads",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_ads, use_container_width=True)

        with col2:
            fig_vehicles = px.bar(
                df_market,
                x="Market",
                y="Unique Vehicles",
                title="Unique Vehicles by Market",
                color="Unique Vehicles",
                color_continuous_scale="Greens",
            )
            st.plotly_chart(fig_vehicles, use_container_width=True)

    # Vehicle model breakdown
    st.subheader("🚗 Top Vehicle Models")

    vehicle_counts = analyzer.df_filtered["vehicle_model"].value_counts().head(10)
    if len(vehicle_counts) > 0:
        fig_vehicles = px.bar(
            x=vehicle_counts.index,
            y=vehicle_counts.values,
            title="Top 10 Vehicle Models by Advertisement Count",
            labels={"x": "Vehicle Model", "y": "Number of Ads"},
        )
        fig_vehicles.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_vehicles, use_container_width=True)


def show_vehicle_analysis(analyzer, selected_market, selected_vehicle):
    """Display detailed vehicle analysis"""
    st.header("🚗 Vehicle Analysis")

    vehicle_stats = analyzer.get_vehicle_analysis()

    if selected_vehicle != "All":
        # Detailed analysis for selected vehicle
        st.subheader(f"📋 Detailed Analysis: {selected_vehicle}")

        if selected_vehicle in vehicle_stats:
            stats = vehicle_stats[selected_vehicle]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Advertisements", stats["total_ads"])
            with col2:
                st.metric("Markets", len(stats["market_breakdown"]))
            with col3:
                st.metric("Unique Advertisers", len(stats["advertisers"]))

            # Market breakdown for this vehicle
            if stats["market_breakdown"]:
                st.subheader("🌍 Market Distribution")
                market_df = pd.DataFrame(
                    list(stats["market_breakdown"].items()),
                    columns=["Market", "Advertisements"],
                )

                fig = px.pie(
                    market_df,
                    values="Advertisements",
                    names="Market",
                    title=f"{selected_vehicle} - Market Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Advertisers list
            st.subheader("📢 Advertisers")
            for i, advertiser in enumerate(stats["advertisers"][:10], 1):
                st.write(f"{i}. {advertiser}")

            if len(stats["advertisers"]) > 10:
                st.write(f"... and {len(stats['advertisers']) - 10} more")

    else:
        # Overview of all vehicles
        st.subheader("📊 All Vehicles Overview")

        # Create comparison table
        comparison_data = []
        for vehicle, stats in vehicle_stats.items():
            if vehicle != "Unknown":
                comparison_data.append(
                    {
                        "Vehicle": vehicle,
                        "Total Ads": stats["total_ads"],
                        "Markets": len(stats["market_breakdown"]),
                        "Advertisers": len(stats["advertisers"]),
                        "Avg Spend": (
                            f"${stats['avg_spend']:.2f}"
                            if stats["avg_spend"] > 0
                            else "N/A"
                        ),
                    }
                )

        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            df_comparison = df_comparison.sort_values("Total Ads", ascending=False)
            st.dataframe(df_comparison, use_container_width=True)


def show_feature_analysis(analyzer, selected_market, selected_vehicle):
    """Display enhanced feature analysis with detailed content"""
    st.header("🎯 Feature Analysis")

    feature_analysis = analyzer.analyze_features_mentioned()

    if not feature_analysis:
        st.warning("No feature analysis data available.")
        return

    # Filter by selected vehicle if specified
    if selected_vehicle != "All" and selected_vehicle in feature_analysis:
        feature_data = {selected_vehicle: feature_analysis[selected_vehicle]}
        st.subheader(f"Features Mentioned for {selected_vehicle}")
    else:
        feature_data = feature_analysis
        st.subheader("Features Mentioned Across All Vehicles")

    # Create feature summary
    all_features = {}
    for vehicle, features in feature_data.items():
        for feature, count in features.items():
            if feature not in all_features:
                all_features[feature] = 0
            all_features[feature] += count

    if all_features:
        # Feature frequency chart
        col1, col2 = st.columns([2, 1])

        with col1:
            feature_df = pd.DataFrame(
                list(all_features.items()), columns=["Feature", "Mentions"]
            ).sort_values("Mentions", ascending=True)

            fig = px.bar(
                feature_df,
                x="Mentions",
                y="Feature",
                orientation="h",
                title="Feature Mentions Frequency",
                color="Mentions",
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 Feature Summary")
            for feature, count in sorted(
                all_features.items(), key=lambda x: x[1], reverse=True
            ):
                st.metric(feature, f"{count} mentions")

        # Enhanced Feature Detail Analysis
        st.subheader("🔍 Detailed Feature Analysis")
        st.markdown(
            "**Click on a feature below to see what advertisers are actually saying about it:**"
        )

        # Create tabs for each feature
        feature_names = sorted(
            all_features.keys(), key=lambda x: all_features[x], reverse=True
        )

        if len(feature_names) > 0:
            # Create tabs for top features
            tabs = st.tabs(
                [f"{feature} ({all_features[feature]})" for feature in feature_names]
            )

            for i, feature in enumerate(feature_names):
                with tabs[i]:
                    show_feature_detail(analyzer, feature, selected_vehicle)

        # Optional: Feature breakdown by vehicle heatmap (if showing all vehicles)
        if selected_vehicle == "All" and len(feature_data) > 1:
            with st.expander(
                "🔍 Feature Breakdown by Vehicle (Heatmap)", expanded=False
            ):
                # Create heatmap data
                vehicles = list(feature_data.keys())[:15]  # Limit to top 15 vehicles
                features = list(all_features.keys())

                heatmap_data = []
                for vehicle in vehicles:
                    row = []
                    for feature in features:
                        count = feature_data[vehicle].get(feature, 0)
                        row.append(count)
                    heatmap_data.append(row)

                fig_heatmap = go.Figure(
                    data=go.Heatmap(
                        z=heatmap_data,
                        x=features,
                        y=vehicles,
                        colorscale="Blues",
                        showscale=True,
                    )
                )

                fig_heatmap.update_layout(
                    title="Feature Mentions Heatmap by Vehicle",
                    xaxis_title="Features",
                    yaxis_title="Vehicles",
                    height=600,
                )

                st.plotly_chart(fig_heatmap, use_container_width=True)


def show_feature_detail(analyzer, feature_category, selected_vehicle):
    """Show detailed analysis for a specific feature"""
    st.subheader(f"💬 What advertisers say about {feature_category}")

    # Get detailed mentions for this feature
    detailed_mentions = analyzer.get_feature_mentions_detail(
        feature_category, selected_vehicle
    )

    if not detailed_mentions:
        st.warning(f"No detailed mentions found for {feature_category}")
        return

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Mentions", len(detailed_mentions))
    with col2:
        unique_vehicles = len(set([m["vehicle_model"] for m in detailed_mentions]))
        st.metric("Vehicles", unique_vehicles)
    with col3:
        unique_advertisers = len(set([m["advertiser"] for m in detailed_mentions]))
        st.metric("Advertisers", unique_advertisers)

    # Show sample mentions
    st.subheader("📝 Sample Mentions")

    # Group by vehicle for better organization
    mentions_by_vehicle = {}
    for mention in detailed_mentions:
        vehicle = mention["vehicle_model"]
        if vehicle not in mentions_by_vehicle:
            mentions_by_vehicle[vehicle] = []
        mentions_by_vehicle[vehicle].append(mention)

    # Display mentions organized by vehicle
    for vehicle, mentions in mentions_by_vehicle.items():
        with st.expander(f"🚗 {vehicle} ({len(mentions)} mentions)", expanded=False):
            for i, mention in enumerate(mentions, 1):  # Show ALL mentions per vehicle
                st.markdown(f"**{i}. {mention['advertiser']}**")
                st.markdown(f"*Keyword matched: {mention['matched_keyword']}*")

                # Show relevant text with highlighting
                relevant_text = mention["relevant_text"]
                if relevant_text:
                    st.markdown(f"📄 **Relevant text:** {relevant_text}")
                else:
                    # Fallback to showing part of full summary
                    full_summary = (
                        mention["full_summary"][:300] + "..."
                        if len(mention["full_summary"]) > 300
                        else mention["full_summary"]
                    )
                    st.markdown(f"📄 **Summary excerpt:** {full_summary}")

                st.markdown("---")

    # Download detailed data
    if st.button(
        f"📥 Download {feature_category} Analysis", key=f"download_{feature_category}"
    ):
        # Create downloadable data
        download_data = []
        for mention in detailed_mentions:
            download_data.append(
                {
                    "Vehicle": mention["vehicle_model"],
                    "Advertiser": mention["advertiser"],
                    "Matched_Keyword": mention["matched_keyword"],
                    "Relevant_Text": mention["relevant_text"],
                    "Full_Summary": mention["full_summary"],
                    "Markets": mention["targeted_countries"],
                    "Date": mention["start_date"],
                }
            )

        df_download = pd.DataFrame(download_data)
        csv = df_download.to_csv(index=False)

        st.download_button(
            label=f"Download {feature_category} mentions as CSV",
            data=csv,
            file_name=f"{feature_category.lower()}_mentions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"download_csv_{feature_category}",
        )


def show_image_analysis(analyzer, selected_market, selected_vehicle):
    """Display image theme analysis"""
    st.header("🖼️ Image Theme Analysis")

    theme_analysis = analyzer.analyze_image_themes()

    if not theme_analysis:
        st.warning("No image theme analysis data available.")
        return

    # Filter by selected vehicle if specified
    if selected_vehicle != "All" and selected_vehicle in theme_analysis:
        theme_data = {selected_vehicle: theme_analysis[selected_vehicle]}
        st.subheader(f"Image Themes for {selected_vehicle}")
    else:
        theme_data = theme_analysis
        st.subheader("Image Themes Across All Vehicles")

    # Aggregate theme data
    all_themes = {}
    for vehicle, themes in theme_data.items():
        for theme, count in themes.items():
            if theme not in all_themes:
                all_themes[theme] = 0
            all_themes[theme] += count

    if all_themes:
        col1, col2 = st.columns(2)

        with col1:
            # Setting/Location themes
            location_themes = {
                k: v for k, v in all_themes.items() if k in ["City", "Country"]
            }
            if location_themes:
                fig_location = px.pie(
                    values=list(location_themes.values()),
                    names=list(location_themes.keys()),
                    title="🏙️ Setting: City vs Country",
                )
                st.plotly_chart(fig_location, use_container_width=True)

            # Focus themes
            focus_themes = {
                k: v
                for k, v in all_themes.items()
                if k in ["Interior Focus", "Exterior Focus"]
            }
            if focus_themes:
                fig_focus = px.pie(
                    values=list(focus_themes.values()),
                    names=list(focus_themes.keys()),
                    title="🎯 Focus: Interior vs Exterior",
                )
                st.plotly_chart(fig_focus, use_container_width=True)

        with col2:
            # Lifestyle themes
            lifestyle_themes = {
                k: v for k, v in all_themes.items() if k in ["Lifestyle", "Commute"]
            }
            if lifestyle_themes:
                fig_lifestyle = px.pie(
                    values=list(lifestyle_themes.values()),
                    names=list(lifestyle_themes.keys()),
                    title="🚗 Purpose: Lifestyle vs Commute",
                )
                st.plotly_chart(fig_lifestyle, use_container_width=True)

            # Style themes
            style_themes = {
                k: v for k, v in all_themes.items() if k in ["Luxury", "Sport"]
            }
            if style_themes:
                fig_style = px.pie(
                    values=list(style_themes.values()),
                    names=list(style_themes.keys()),
                    title="✨ Style: Luxury vs Sport",
                )
                st.plotly_chart(fig_style, use_container_width=True)

        # Overall theme distribution
        st.subheader("📊 All Image Themes")
        theme_df = pd.DataFrame(
            list(all_themes.items()), columns=["Theme", "Count"]
        ).sort_values("Count", ascending=True)

        fig_all_themes = px.bar(
            theme_df,
            x="Count",
            y="Theme",
            orientation="h",
            title="Image Theme Distribution",
            color="Count",
            color_continuous_scale="Plasma",
        )
        st.plotly_chart(fig_all_themes, use_container_width=True)


def show_meta_analysis(analyzer, selected_market, selected_vehicle):
    """Display meta analysis of style, tone, and themes"""
    st.header("📝 Meta Analysis")

    tone_analysis = analyzer.analyze_tone_and_style()

    if not tone_analysis:
        st.warning("No tone and style analysis data available.")
        return

    # Filter by selected vehicle if specified
    if selected_vehicle != "All" and selected_vehicle in tone_analysis:
        tone_data = {selected_vehicle: tone_analysis[selected_vehicle]}
        st.subheader(f"Style & Tone Analysis for {selected_vehicle}")
    else:
        tone_data = tone_analysis
        st.subheader("Style & Tone Analysis Across All Vehicles")

    # Aggregate tone data
    all_tones = {}
    for vehicle, tones in tone_data.items():
        for tone, count in tones.items():
            if tone not in all_tones:
                all_tones[tone] = 0
            all_tones[tone] += count

    if all_tones:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎨 Style & Tone Distribution")
            tone_df = pd.DataFrame(
                list(all_tones.items()), columns=["Tone", "Count"]
            ).sort_values("Count", ascending=False)

            fig_tone = px.bar(
                tone_df,
                x="Tone",
                y="Count",
                title="Style & Tone Frequency",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig_tone.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tone, use_container_width=True)

        with col2:
            st.subheader("🎯 Top Tone Characteristics")
            for i, (tone, count) in enumerate(tone_df.head(5).values, 1):
                st.markdown(f"**{i}. {tone}** - {count} mentions")

    # Detailed vehicle comparison (if showing all vehicles)
    if selected_vehicle == "All" and len(tone_data) > 1:
        st.subheader("🔍 Style & Tone by Vehicle")

        # Create comparison matrix
        vehicles = list(tone_data.keys())[:10]  # Limit to top 10 vehicles
        tones = list(all_tones.keys())

        comparison_data = []
        for vehicle in vehicles:
            row_data = {"Vehicle": vehicle}
            for tone in tones:
                row_data[tone] = tone_data[vehicle].get(tone, 0)
            comparison_data.append(row_data)

        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)

    # Summary insights
    st.subheader("💡 Key Insights")

    if all_tones:
        top_tone = max(all_tones, key=all_tones.get)
        total_mentions = sum(all_tones.values())

        insights = [
            f"**Most Common Style/Tone:** {top_tone} ({all_tones[top_tone]} mentions)",
            f"**Total Style Mentions:** {total_mentions}",
            f"**Style Diversity:** {len(all_tones)} different tones identified",
        ]

        for insight in insights:
            st.markdown(f"• {insight}")

    # Export functionality
    st.subheader("📥 Export Analysis")

    if st.button("Generate Analysis Report"):
        # Create comprehensive report
        report_data = {
            "market_summary": analyzer.get_market_summary(),
            "vehicle_analysis": analyzer.get_vehicle_analysis(),
            "feature_analysis": analyzer.analyze_features_mentioned(),
            "image_themes": analyzer.analyze_image_themes(),
            "tone_analysis": analyzer.analyze_tone_and_style(),
        }

        # Convert to JSON for download
        report_json = json.dumps(report_data, indent=2, default=str)

        st.download_button(
            label="Download Analysis Report (JSON)",
            data=report_json,
            file_name=f"ev_advert_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

        st.success("✅ Analysis report generated successfully!")


if __name__ == "__main__":
    main()
