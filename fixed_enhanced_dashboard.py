#!/usr/bin/env python3
"""
Enhanced EV Advertisement Analysis Dashboard - Fixed Version
Advanced Streamlit dashboard with image URLs and analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import os
import hashlib
import requests
from collections import Counter
from PIL import Image
from io import BytesIO
from pathlib import Path
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Enhanced EV Advertisement Analysis",
    page_icon="🚗⚡",
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
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def parse_openai_features(features_json):
    """Parse OpenAI features JSON string"""
    if pd.isna(features_json) or features_json == "":
        return {}
    try:
        return json.loads(features_json)
    except:
        return {}


@st.cache_data
def load_enhanced_data():
    """Load the complete dataset from chunked CSV files in Data/ directory"""
    try:
        data_dir = Path("Data")

        # First try to load from chunked data
        if data_dir.exists():
            # Load the combined target vehicles file if it exists
            combined_file = data_dir / "target_vehicles_combined.csv"
            if combined_file.exists():
                df = pd.read_csv(combined_file)
                return df

            # Otherwise, load and combine individual chunks
            csv_files = list(data_dir.glob("*.csv"))
            csv_files = [f for f in csv_files if f.name != "metadata.json"]

            if csv_files:
                dataframes = []
                for csv_file in csv_files:
                    if csv_file.name not in [
                        "metadata.json",
                        "target_vehicles_combined.csv",
                    ]:
                        chunk_df = pd.read_csv(csv_file)
                        dataframes.append(chunk_df)

                if dataframes:
                    df = pd.concat(dataframes, ignore_index=True)
                    return df

        # Fallback to original file if chunked data not available
        original_file = "ev_ads_complete_with_images_and_gender_20250720_100525.csv"
        if os.path.exists(original_file):
            df = pd.read_csv(original_file)
            return df

        st.error(
            "❌ No data files found. Please ensure Data/ directory contains CSV files or the original dataset exists."
        )
        return None

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None


def parse_openai_features(features_json):
    """Parse OpenAI features JSON string"""
    if pd.isna(features_json) or features_json == "":
        return {}
    try:
        return json.loads(features_json)
    except:
        return {}


def find_local_image_exact(ad_id, image_url):
    """Find locally saved image for an ad using exact hash matching"""
    # Generate the same filename used in download scripts
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
    filename = f"{ad_id}_{url_hash}.jpg"

    # Check possible local directories
    local_dirs = [
        "ev_ad_images/by_car_model",
        "ev_ad_images/thumbnails",
        "sample_images",
        "downloaded_images/originals",
    ]

    for base_dir in local_dirs:
        if os.path.exists(base_dir):
            # Search in subdirectories
            for root, dirs, files in os.walk(base_dir):
                if filename in files:
                    return os.path.join(root, filename)

            # Also check direct filename match
            direct_path = os.path.join(base_dir, filename)
            if os.path.exists(direct_path):
                return direct_path

    return None


def find_local_image_by_ad_id(ad_id):
    """Find locally saved image for an ad by ad_id only (ignoring hash)"""
    # Check possible local directories
    local_dirs = [
        "ev_ad_images/by_car_model",
        "ev_ad_images/thumbnails",
        "sample_images",
        "downloaded_images/originals",
    ]

    for base_dir in local_dirs:
        if os.path.exists(base_dir):
            # Search in subdirectories
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    # Check if filename starts with ad_id followed by underscore
                    if file.startswith(f"{ad_id}_") and file.lower().endswith(
                        (".jpg", ".jpeg", ".png")
                    ):
                        return os.path.join(root, file)

    return None


def find_local_image(ad_id, image_url):
    """Find locally saved image - try exact match first, then ad_id only"""
    # First try exact hash matching
    exact_path = find_local_image_exact(ad_id, image_url)
    if exact_path:
        return exact_path

    # If no exact match, try ad_id only matching
    ad_id_path = find_local_image_by_ad_id(ad_id)
    if ad_id_path:
        return ad_id_path

    return None


def load_image_from_url(image_url):
    """Load image from URL"""
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image
    except Exception as e:
        return None
    return None


def load_image_local_or_url(ad_id, image_url, prefer_local=True):
    """Load image from local file first (flexible matching), fallback to URL"""

    if prefer_local and pd.notna(image_url):
        # Try to find local image first (with flexible matching)
        local_path = find_local_image(ad_id, image_url)
        if local_path:
            try:
                image = Image.open(local_path)
                return image, "local"
            except Exception as e:
                pass  # Fall back to URL

    # Fallback to URL loading
    if pd.notna(image_url):
        image = load_image_from_url(image_url)
        if image:
            return image, "url"

    return None, "failed"


def display_ad_image(row, prefer_local=True, max_width=300):
    """Display an ad image using local file first, fallback to URL"""

    ad_id = row.get("ad_id", "Unknown")
    image_url = row.get("image_url")
    advertiser = row.get("advertiser_name", "Unknown")
    vehicle = row.get("primary_vehicle", "Unknown")

    # Create a cleaner container for the image and info
    with st.container():
        if pd.notna(image_url):
            # Try to load image (local first, then URL)
            image, source = load_image_local_or_url(ad_id, image_url, prefer_local)

            if image:
                source_emoji = "💾" if source == "local" else "🌐"

                # Display image with full width
                st.image(image, use_container_width=True)

                # Display info in a compact format below the image
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{advertiser}** - {vehicle}")
                    st.caption(f"Ad ID: {ad_id}")
                    if pd.notna(row.get("primary_country")):
                        st.caption(f"Country: {row['primary_country']}")
                with col2:
                    if source == "local":
                        st.success("💾 Local")
                    else:
                        st.info("🌐 URL")

                # Show additional info if available
                if pd.notna(row.get("gpt4_text_analysis")):
                    with st.expander("🤖 GPT-4 Analysis"):
                        st.text(str(row["gpt4_text_analysis"])[:300] + "...")

            else:
                st.error("❌ Failed to load image")
                st.caption(f"{advertiser} - {vehicle} (Ad ID: {ad_id})")
                st.write(f"Image URL: {image_url[:50]}...")
        else:
            st.warning("No image URL available")
            st.caption(f"{advertiser} - {vehicle} (Ad ID: {ad_id})")


def create_image_gallery(df, title="Image Gallery", max_images=12):
    """Create an image gallery from dataframe with image URLs"""
    st.subheader(title)

    # Filter to only ads with image URLs
    df_with_images = df[df["image_url"].notna()].copy()

    if len(df_with_images) == 0:
        st.warning("No images available for the selected filters.")
        return

    # Limit number of images to display
    df_display = df_with_images.head(max_images)

    st.write(f"Showing {len(df_display)} of {len(df_with_images)} available images")

    # Create columns for gallery layout
    cols_per_row = 3
    rows = (len(df_display) + cols_per_row - 1) // cols_per_row

    for row_idx in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            img_idx = row_idx * cols_per_row + col_idx
            if img_idx < len(df_display):
                with cols[col_idx]:
                    display_ad_image(df_display.iloc[img_idx], max_width=250)


def create_image_gallery_with_preference(
    df,
    title="Image Gallery",
    max_images=12,
    prefer_local=True,
    prioritize_local_display=True,
):
    """Create an image gallery with local/URL preference"""
    st.subheader(title)

    # Filter to only ads with image URLs
    df_with_images = df[df["image_url"].notna()].copy()

    if len(df_with_images) == 0:
        st.warning("No images available for the selected filters.")
        return

    # Remove duplicate ad_ids to avoid showing the same image multiple times
    df_with_images = df_with_images.drop_duplicates(subset=["ad_id"], keep="first")

    # If prioritize_local_display is True, prioritize records with local images
    if prioritize_local_display:
        # Check which records have local images
        df_with_images["has_local_image"] = df_with_images.apply(
            lambda row: find_local_image_by_ad_id(str(row["ad_id"])) is not None, axis=1
        )

        # Sort by has_local_image (True first), then by index
        df_with_images = df_with_images.sort_values(
            ["has_local_image"], ascending=False
        )

        # Show local image statistics
        local_available = df_with_images["has_local_image"].sum()
        st.info(
            f"💾 {local_available} ads have local images available out of {len(df_with_images)} total"
        )

    # Limit number of images to display
    df_display = df_with_images.head(max_images)

    # Count local vs URL images
    local_count = 0
    url_count = 0
    failed_count = 0

    for idx, row in df_display.iterrows():
        ad_id = row.get("ad_id", "Unknown")
        image_url = row.get("image_url")
        if pd.notna(image_url):
            image, source = load_image_local_or_url(ad_id, image_url, prefer_local)
            if source == "local":
                local_count += 1
            elif source == "url":
                url_count += 1
            else:
                failed_count += 1

    # Display statistics in a clean format
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📸 Total Images", len(df_display))
    with col2:
        st.metric("💾 Local", local_count)
    with col3:
        st.metric("🌐 URL", url_count)
    with col4:
        st.metric("❌ Failed", failed_count)

    st.write(f"Showing {len(df_display)} of {len(df_with_images)} unique ads")

    # Create a cleaner gallery layout with better spacing
    cols_per_row = 2  # Reduced to 2 columns for better visibility

    for i in range(0, len(df_display), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(df_display):
                with cols[j]:
                    row = df_display.iloc[i + j]

                    # Create a card-like container for each image
                    with st.container():
                        st.markdown("---")  # Separator line

                        # Display the image with better formatting
                        display_ad_image(
                            row,
                            prefer_local=prefer_local,
                            max_width=350,
                        )


def clean_brand_names(text, vehicle_name):
    """Remove brand names and model names from text"""
    if pd.isna(text):
        return ""

    # Convert to string and clean
    text = str(text).lower()

    # Remove common brand names and model names
    brands_to_remove = [
        "volkswagen",
        "vw",
        "tesla",
        "audi",
        "bmw",
        "hyundai",
        "ioniq",
        "id.4",
        "id4",
        "model y",
        "q4 e-tron",
        "ix1",
        "ix3",
    ]

    for brand in brands_to_remove:
        text = re.sub(rf"\b{re.escape(brand)}\b", "", text, flags=re.IGNORECASE)

    # Remove extra whitespace
    cleaned_text = re.sub(r"\s+", " ", text).strip()

    # Remove very short words (less than 3 characters)
    words = cleaned_text.split()
    words = [word for word in words if len(word) >= 3]
    cleaned_text = " ".join(words)

    # Remove duplicate consecutive words
    words = cleaned_text.split()
    cleaned_words = []
    prev_word = ""
    for word in words:
        if word != prev_word:
            cleaned_words.append(word)
        prev_word = word

    cleaned_text = " ".join(cleaned_words)

    return cleaned_text


def main():
    # Clean interface - no header needed

    # Load data
    df = load_enhanced_data()
    if df is None:
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Vehicle filter
    vehicles = ["All"] + sorted(df["primary_vehicle"].unique().tolist())
    selected_vehicle = st.sidebar.selectbox("Select Vehicle", vehicles)

    # Country filter
    countries = ["All"] + sorted(df["primary_country"].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", countries)

    # Advertiser type filter
    advertiser_types = ["All"] + sorted(df["advertiser_name"].unique().tolist())
    selected_advertiser = st.sidebar.selectbox("Select Advertiser", advertiser_types)

    # Gender targeting filter (if available)
    if "primary_gender_target" in df.columns:
        gender_targets = ["All"] + sorted(df["primary_gender_target"].unique().tolist())
        selected_gender = st.sidebar.selectbox("Gender Targeting", gender_targets)
    else:
        selected_gender = "All"

    # Apply filters
    filtered_df = df.copy()

    if selected_vehicle != "All":
        filtered_df = filtered_df[filtered_df["primary_vehicle"] == selected_vehicle]

    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["primary_country"] == selected_country]

    if selected_advertiser != "All":
        filtered_df = filtered_df[filtered_df["advertiser_name"] == selected_advertiser]

    if selected_gender != "All" and "primary_gender_target" in df.columns:
        filtered_df = filtered_df[
            filtered_df["primary_gender_target"] == selected_gender
        ]

    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Ads", len(filtered_df))

    with col2:
        if "openai_features" in filtered_df.columns:
            ads_with_features = filtered_df["openai_features"].notna().sum()
            st.metric(
                "Ads with Features",
                f"{ads_with_features} ({ads_with_features/len(filtered_df)*100:.1f}%)",
            )
        else:
            ads_with_gpt4 = filtered_df["gpt4_text_analysis"].notna().sum()
            st.metric(
                "Ads with GPT-4 Analysis",
                f"{ads_with_gpt4} ({ads_with_gpt4/len(filtered_df)*100:.1f}%)",
            )

    with col3:
        if "has_gender_targeting" in filtered_df.columns:
            ads_with_gender = filtered_df["has_gender_targeting"].sum()
            st.metric(
                "Ads with Gender Data",
                f"{ads_with_gender} ({ads_with_gender/len(filtered_df)*100:.1f}%)",
            )
        else:
            ads_with_images = filtered_df["image_url"].notna().sum()
            st.metric(
                "Ads with Images",
                f"{ads_with_images} ({ads_with_images/len(filtered_df)*100:.1f}%)",
            )

    with col4:
        unique_advertisers = filtered_df["advertiser_name"].nunique()
        st.metric("Unique Advertisers", unique_advertisers)

    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "🎯 Gender Targeting",
            "🔧 Feature Analysis",
            "🖼️ Image Gallery",
            "📈 Advanced Analytics",
        ]
    )

    with tab1:
        st.header("📊 Overview")

        col1, col2 = st.columns(2)

        with col1:
            # Vehicle distribution
            vehicle_counts = filtered_df["primary_vehicle"].value_counts()
            fig_vehicles = px.bar(
                x=vehicle_counts.values,
                y=vehicle_counts.index,
                orientation="h",
                title="Ads by Vehicle Model",
                labels={"x": "Number of Ads", "y": "Vehicle Model"},
            )
            st.plotly_chart(fig_vehicles, use_container_width=True)

        with col2:
            # Country distribution
            country_counts = filtered_df["primary_country"].value_counts()
            fig_countries = px.pie(
                values=country_counts.values,
                names=country_counts.index,
                title="Ads by Country",
            )
            st.plotly_chart(fig_countries, use_container_width=True)

        # Advertiser analysis
        st.subheader("Top Advertisers")
        advertiser_counts = filtered_df["advertiser_name"].value_counts().head(10)
        fig_advertisers = px.bar(
            x=advertiser_counts.values,
            y=advertiser_counts.index,
            orientation="h",
            title="Top 10 Advertisers by Ad Count",
        )
        st.plotly_chart(fig_advertisers, use_container_width=True)

    with tab2:
        st.header("🎯 Gender Targeting Analysis")

        # Check if gender targeting data is available
        if (
            "has_gender_targeting" in filtered_df.columns
            and "primary_gender_target" in filtered_df.columns
        ):
            # Gender targeting overview
            gender_data = filtered_df[filtered_df["has_gender_targeting"] == True]

            if len(gender_data) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    # Gender targeting by vehicle
                    gender_vehicle = (
                        gender_data.groupby(
                            ["primary_vehicle", "primary_gender_target"]
                        )
                        .size()
                        .unstack(fill_value=0)
                    )
                    fig_gender_vehicle = px.bar(
                        gender_vehicle,
                        title="Gender Targeting by Vehicle Model",
                        labels={"value": "Number of Ads", "index": "Vehicle Model"},
                    )
                    st.plotly_chart(fig_gender_vehicle, use_container_width=True)

                with col2:
                    # Gender targeting distribution
                    gender_dist = gender_data["primary_gender_target"].value_counts()
                    fig_gender_dist = px.pie(
                        values=gender_dist.values,
                        names=gender_dist.index,
                        title="Gender Targeting Distribution",
                    )
                    st.plotly_chart(fig_gender_dist, use_container_width=True)

                # Gender targeting insights
                st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                st.write("**🔍 Gender Targeting Insights:**")

                male_dominant = gender_data[
                    gender_data["primary_gender_target"] == "Male"
                ]
                female_dominant = gender_data[
                    gender_data["primary_gender_target"] == "Female"
                ]
                mixed_targeting = gender_data[
                    gender_data["primary_gender_target"] == "Mixed"
                ]

                st.write(
                    f"• **Male-targeted ads**: {len(male_dominant)} ({len(male_dominant)/len(gender_data)*100:.1f}%)"
                )
                st.write(
                    f"• **Female-targeted ads**: {len(female_dominant)} ({len(female_dominant)/len(gender_data)*100:.1f}%)"
                )
                st.write(
                    f"• **Mixed targeting**: {len(mixed_targeting)} ({len(mixed_targeting)/len(gender_data)*100:.1f}%)"
                )

                if len(male_dominant) > len(female_dominant):
                    st.write(
                        "• **Opportunity**: Strong male bias suggests potential for female-targeted campaigns"
                    )

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("No gender targeting data available for current filters")
        else:
            st.warning("Gender targeting data is not available in this dataset.")

    with tab3:
        st.header("🔧 Feature Analysis")

        # Check if OpenAI features are available
        if "openai_features" in filtered_df.columns:
            st.subheader("OpenAI Feature Analysis")
            # Parse OpenAI features
            feature_data = []
            for idx, row in filtered_df.iterrows():
                features = parse_openai_features(row["openai_features"])
                for category, details in features.items():
                    # Handle case where details might be a string instead of dict
                    if isinstance(details, dict):
                        feature_data.append(
                            {
                                "vehicle": row["primary_vehicle"],
                                "country": row["primary_country"],
                                "category": category,
                                "claim": details.get("claim", ""),
                                "positioning": details.get("positioning", ""),
                                "tone": details.get("tone", ""),
                                "source": details.get("source", ""),
                            }
                        )
                    else:
                        # If details is a string, create a basic entry
                        feature_data.append(
                            {
                                "vehicle": row["primary_vehicle"],
                                "country": row["primary_country"],
                                "category": category,
                                "claim": str(details),
                                "positioning": "unknown",
                                "tone": "unknown",
                                "source": "unknown",
                            }
                        )

            if feature_data:
                features_df = pd.DataFrame(feature_data)

                col1, col2 = st.columns(2)

                with col1:
                    # Feature category frequency (filter out categories with less than 10 mentions and remove "error")
                    category_counts = features_df["category"].value_counts()
                    # Remove "error" category and only include categories with 10 or more mentions
                    category_counts = category_counts[category_counts.index != "error"]
                    category_counts = category_counts[
                        category_counts.index != "Analysis Themes"
                    ]
                    filtered_categories = category_counts[category_counts >= 12]

                    if len(filtered_categories) > 0:
                        fig_categories = px.bar(
                            x=filtered_categories.values,
                            y=filtered_categories.index,
                            orientation="h",
                            title="Top Themes",
                        )

                        # Customize the chart layout
                        fig_categories.update_layout(
                            xaxis_title="Number of Mentions",  # Remove x-axis title
                            yaxis_title="Themes (Features)",  # Remove y-axis title
                            yaxis=dict(
                                tickmode="linear",  # Show all tick labels
                                dtick=1,  # Show every category
                            ),
                            showlegend=False,
                            margin=dict(l=20, r=20, t=40, b=20),
                        )

                        st.plotly_chart(fig_categories, use_container_width=True)
                    else:
                        st.warning("No feature categories with 10+ mentions found")

                with col2:
                    # Feature positioning analysis
                    positioning_counts = (
                        features_df["positioning"].value_counts().head(8)
                    )
                    positioning_counts = positioning_counts[
                        positioning_counts.index != "unknown"
                    ]

                    if len(positioning_counts) > 0:
                        fig_positioning = px.pie(
                            values=positioning_counts.values,
                            names=positioning_counts.index,
                            title="Feature Positioning Strategies",
                        )
                        st.plotly_chart(fig_positioning, use_container_width=True)

                # Feature analysis by vehicle - use full width below the two columns
                st.subheader("Feature Analysis by Vehicle")
                vehicle_features = (
                    features_df.groupby(["vehicle", "category"])
                    .size()
                    .unstack(fill_value=0)
                )

                # Rotate the heatmap 90 degrees by swapping x and y
                fig_vehicle_features = px.imshow(
                    vehicle_features.T.values,  # Transpose to rotate 90 degrees
                    x=vehicle_features.index,  # Vehicles on x-axis
                    y=vehicle_features.columns,  # Categories on y-axis
                    title="Feature Mentions by Vehicle (Rotated View)",
                    color_continuous_scale="Blues",
                    aspect="auto",
                )
                fig_vehicle_features.update_layout(
                    xaxis_title="Mentions",
                    yaxis_title="Features",
                    height=500,
                    xaxis=dict(tickmode="linear", tick0=0, dtick=1),
                    yaxis=dict(tickmode="linear", tick0=0, dtick=1),
                )
                st.plotly_chart(fig_vehicle_features, use_container_width=True)

                # Detailed Feature Breakdown
                st.subheader("📋 Detailed Feature Breakdown")
                st.write(
                    "Click on any feature to see the ads that mention it and their details."
                )

                # First, let's get the source_text for each feature by merging back with original data
                # Add ad_id to features_df to link back to original data
                features_with_source = []
                for idx, row in filtered_df.iterrows():
                    if pd.notna(row["openai_features"]):
                        features = parse_openai_features(row["openai_features"])
                        for category, details in features.items():
                            if isinstance(details, dict):
                                # The structure is category -> details (not category -> claim_key -> details)
                                features_with_source.append(
                                    {
                                        "ad_id": row["ad_id"],
                                        "category": category,
                                        "claim": details.get("claim", "Unknown claim"),
                                        "vehicle": row["primary_vehicle"],
                                        "country": row["primary_country"],
                                        "positioning": details.get(
                                            "positioning", "unknown"
                                        ),
                                        "tone": details.get("tone", "unknown"),
                                        "source": details.get("source", "unknown"),
                                        "source_text": details.get(
                                            "source", "unknown"
                                        ),  # Store the source field name
                                        "actual_source_content": str(
                                            row.get(details.get("source", ""), "") or ""
                                        ),  # Get actual content from that field
                                        "advertiser": row.get(
                                            "advertiser_name", "Unknown"
                                        ),
                                    }
                                )

                if features_with_source:
                    features_with_source_df = pd.DataFrame(features_with_source)

                    # Group features by category and claim, collecting all source texts
                    feature_summary = (
                        features_with_source_df.groupby(["category", "claim"])
                        .agg(
                            {
                                "vehicle": lambda x: list(x.unique()),
                                "country": lambda x: list(x.unique()),
                                "positioning": lambda x: list(x.unique()),
                                "tone": lambda x: list(x.unique()),
                                "source": lambda x: list(x.unique()),
                                "source_text": lambda x: list(x.unique()),
                                "actual_source_content": lambda x: list(x.unique()),
                                "advertiser": lambda x: list(x.unique()),
                                "ad_id": lambda x: list(x.unique()),
                            }
                        )
                        .reset_index()
                    )

                    # Add ad count for each feature
                    feature_summary["ad_count"] = (
                        features_with_source_df.groupby(["category", "claim"])
                        .size()
                        .values
                    )

                    # Sort by ad count (most mentioned features first)
                    feature_summary = feature_summary.sort_values(
                        "ad_count", ascending=False
                    )

                    # Filter out categories with "error" and claims that are too generic
                    feature_summary = feature_summary[
                        (feature_summary["category"] != "error")
                        & (
                            feature_summary["claim"].str.len() > 5
                        )  # Remove very short claims
                        & (
                            ~feature_summary["claim"].str.contains(
                                "unknown|error|n/a", case=False, na=False
                            )
                        )
                    ]

                    # Add filtering controls for detailed breakdown
                    st.subheader("🔍 Filter Features")
                    col_filter1, col_filter2 = st.columns(2)

                    with col_filter1:
                        # Vehicle filter (sync with sidebar)
                        breakdown_vehicle_filter = st.selectbox(
                            "Filter by vehicle:",
                            ["All"]
                            + sorted(
                                features_with_source_df["vehicle"].unique().tolist()
                            ),
                            key="breakdown_vehicle_filter",
                            index=(
                                0
                                if selected_vehicle == "All"
                                else (
                                    (
                                        ["All"]
                                        + sorted(
                                            features_with_source_df["vehicle"]
                                            .unique()
                                            .tolist()
                                        )
                                    ).index(selected_vehicle)
                                    if selected_vehicle
                                    in features_with_source_df["vehicle"].unique()
                                    else 0
                                )
                            ),
                        )

                    with col_filter2:
                        # Country filter (sync with sidebar)
                        breakdown_country_filter = st.selectbox(
                            "Filter by country:",
                            ["All"]
                            + sorted(
                                features_with_source_df["country"].unique().tolist()
                            ),
                            key="breakdown_country_filter",
                            index=(
                                0
                                if selected_country == "All"
                                else (
                                    (
                                        ["All"]
                                        + sorted(
                                            features_with_source_df["country"]
                                            .unique()
                                            .tolist()
                                        )
                                    ).index(selected_country)
                                    if selected_country
                                    in features_with_source_df["country"].unique()
                                    else 0
                                )
                            ),
                        )

                    # Apply filters to feature data
                    filtered_features_df = features_with_source_df.copy()
                    if breakdown_vehicle_filter != "All":
                        filtered_features_df = filtered_features_df[
                            filtered_features_df["vehicle"] == breakdown_vehicle_filter
                        ]
                    if breakdown_country_filter != "All":
                        filtered_features_df = filtered_features_df[
                            filtered_features_df["country"] == breakdown_country_filter
                        ]

                    # Recalculate feature summary with filtered data
                    if len(filtered_features_df) > 0:
                        filtered_feature_summary = (
                            filtered_features_df.groupby(["category", "claim"])
                            .agg(
                                {
                                    "vehicle": lambda x: list(x.unique()),
                                    "country": lambda x: list(x.unique()),
                                    "positioning": lambda x: list(x.unique()),
                                    "tone": lambda x: list(x.unique()),
                                    "source": lambda x: list(x.unique()),
                                    "source_text": lambda x: list(x.unique()),
                                    "actual_source_content": lambda x: list(x.unique()),
                                    "advertiser": lambda x: list(x.unique()),
                                    "ad_id": lambda x: list(x.unique()),
                                }
                            )
                            .reset_index()
                        )

                        # Add ad count for filtered features
                        filtered_feature_summary["ad_count"] = (
                            filtered_features_df.groupby(["category", "claim"])
                            .size()
                            .values
                        )

                        # Sort by ad count
                        filtered_feature_summary = filtered_feature_summary.sort_values(
                            "ad_count", ascending=False
                        )

                        # Filter out generic claims
                        filtered_feature_summary = filtered_feature_summary[
                            (filtered_feature_summary["category"] != "error")
                            & (filtered_feature_summary["claim"].str.len() > 5)
                            & (
                                ~filtered_feature_summary["claim"].str.contains(
                                    "unknown|error|n/a", case=False, na=False
                                )
                            )
                        ]

                        # Display features grouped by category
                        categories = filtered_feature_summary["category"].unique()

                        for category in categories:
                            if category and category != "error":
                                category_features = filtered_feature_summary[
                                    filtered_feature_summary["category"] == category
                                ]
                                total_ads_in_category = category_features[
                                    "ad_count"
                                ].sum()

                                with st.expander(
                                    f"🔧 {category.title()} ",
                                    expanded=False,
                                ):
                                    st.caption(
                                        f"📊 {len(category_features)} total ad mentions in this category"
                                    )
                                    for idx, row in category_features.iterrows():
                                        claim = row["claim"]
                                        ad_count = row["ad_count"]
                                        vehicles = ", ".join(
                                            [
                                                v
                                                for v in row["vehicle"]
                                                if v and v != "unknown"
                                            ]
                                        )
                                        countries = ", ".join(
                                            [
                                                c
                                                for c in row["country"]
                                                if c and c != "unknown"
                                            ]
                                        )
                                        positioning = ", ".join(
                                            [
                                                p
                                                for p in row["positioning"]
                                                if p and p != "unknown"
                                            ]
                                        )
                                        tone = ", ".join(
                                            [
                                                t
                                                for t in row["tone"]
                                                if t and t != "unknown"
                                            ]
                                        )
                                        source = ", ".join(
                                            [
                                                s
                                                for s in row["source"]
                                                if s and s != "unknown"
                                            ]
                                        )

                                        # Get source texts and advertisers
                                        source_field_names = row.get("source_text", [])
                                        actual_contents = row.get(
                                            "actual_source_content", []
                                        )
                                        advertisers = row.get("advertiser", [])
                                        ad_ids = row.get("ad_id", [])

                                        # Make each feature collapsible
                                        feature_title = (
                                            f"{claim[:60]}..."
                                            if len(claim) > 60
                                            else claim
                                        )
                                        with st.expander(
                                            f"📋 {feature_title} ",
                                            expanded=False,
                                        ):
                                            # Show all details together
                                            st.write(f"**Claim:** {claim}")
                                            if source:
                                                st.write(f"**Source:** {source}")
                                            if countries:
                                                st.write(f"**Countries:** {countries}")
                                            if vehicles:
                                                st.write(f"**Vehicles:** {vehicles}")
                                            if positioning:
                                                st.write(
                                                    f"**Positioning:** {positioning}"
                                                )
                                            if tone:
                                                st.write(f"**Tone:** {tone}")

                                            # Show just one source text example
                                            if actual_contents and any(
                                                content.strip()
                                                for content in actual_contents
                                            ):
                                                # Find the first non-empty source content
                                                for i, (
                                                    content,
                                                    advertiser,
                                                    ad_id,
                                                ) in enumerate(
                                                    zip(
                                                        actual_contents,
                                                        advertisers,
                                                        ad_ids,
                                                    )
                                                ):
                                                    if content.strip():
                                                        # Get the source field name
                                                        source_field = (
                                                            source_field_names[i]
                                                            if i
                                                            < len(source_field_names)
                                                            else "unknown"
                                                        )

                                                        st.write(
                                                            f"**Source Text:** (from {source_field})"
                                                        )
                                                        st.text_area(
                                                            "Source content",
                                                            content,
                                                            height=150,
                                                            key=f"source_{category}_{idx}",
                                                            label_visibility="collapsed",
                                                        )
                                                        break  # Only show the first one
                                    else:
                                        st.warning(
                                            "No features found with current filters"
                                        )
                else:
                    st.warning("No feature analysis data available for current filters")
        else:
            st.warning("OpenAI feature analysis data is not available in this dataset.")
            st.info(
                "This dataset contains GPT-4 image analysis instead. Check the Image Gallery tab for GPT-4 insights."
            )

    with tab4:
        st.header("🖼️ Image Gallery")

        # Show image URL statistics
        total_with_images = filtered_df["image_url"].notna().sum()
        st.info(f"📸 {total_with_images} ads have image URLs in current selection")

        # Add filtering controls for image gallery
        col_img1, col_img2, col_img3, col_img4 = st.columns(4)

        with col_img1:
            # Vehicle filter for images
            img_vehicle_filter = st.selectbox(
                "Filter by vehicle:",
                ["All"] + sorted(filtered_df["primary_vehicle"].unique().tolist()),
                key="img_vehicle_filter",
            )

        with col_img2:
            # Country filter for images
            img_country_filter = st.selectbox(
                "Filter by country:",
                ["All"] + sorted(filtered_df["primary_country"].unique().tolist()),
                key="img_country_filter",
            )

        with col_img3:
            # Number of images to show
            img_count = st.selectbox(
                "Images to show:", [6, 12, 24, 48], index=1, key="img_count"
            )

        with col_img4:
            # Image source preference
            prefer_local = st.checkbox(
                "Prefer local images",
                value=True,
                help="Try local files first, fallback to URLs",
            )

            # Prioritize local images in display order
            prioritize_local = st.checkbox(
                "Show local images first",
                value=True,
                help="Display ads with local images at the top",
            )

        # Apply filters to get image data
        img_filtered_df = filtered_df.copy()

        if img_vehicle_filter != "All":
            img_filtered_df = img_filtered_df[
                img_filtered_df["primary_vehicle"] == img_vehicle_filter
            ]

        if img_country_filter != "All":
            img_filtered_df = img_filtered_df[
                img_filtered_df["primary_country"] == img_country_filter
            ]

        # Filter to only ads with image URLs
        img_filtered_df = img_filtered_df[img_filtered_df["image_url"].notna()]

        # Display the image gallery using the new function
        if len(img_filtered_df) > 0:
            st.markdown(
                f"**📊 Showing up to {img_count} ads from {len(img_filtered_df)} available**"
            )

            # Use the new image gallery function with local preference
            # Pass the full filtered dataset - the function will handle sampling and sorting
            create_image_gallery_with_preference(
                img_filtered_df,
                title="🖼️ Advertisement Images",
                max_images=img_count,
                prefer_local=prefer_local,
                prioritize_local_display=prioritize_local,
            )

            # Show GPT-4 analysis summary if available
            ads_with_analysis = img_filtered_df[
                img_filtered_df["gpt4_text_analysis"].notna()
            ]
            if len(ads_with_analysis) > 0:
                st.subheader("🤖 GPT-4 Image Analysis Insights")

                # Show a few sample analyses
                for i, (idx, row) in enumerate(ads_with_analysis.head(3).iterrows()):
                    with st.expander(
                        f"Analysis {i+1}: {row['primary_vehicle']} - {row['advertiser_name']}"
                    ):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if pd.notna(row["image_url"]):
                                st.image(row["image_url"], width=200)
                        with col2:
                            st.text(str(row["gpt4_text_analysis"])[:800] + "...")
        else:
            st.warning("No ads found for the current filters.")

    with tab5:
        st.header("📈 Advanced Analytics")

        # Text analysis
        st.subheader("📝 Text Analysis")

        # Analyze ad titles
        if "ad_title" in filtered_df.columns:
            titles = filtered_df["ad_title"].dropna()
            if len(titles) > 0:
                # Word frequency analysis
                all_text = " ".join(titles.astype(str))
                words = re.findall(r"\b\w+\b", all_text.lower())
                word_freq = Counter(words)

                # Define automotive jargon and technical terms to highlight
                automotive_jargon = {
                    # Performance terms
                    "horsepower",
                    "hp",
                    "torque",
                    "acceleration",
                    "0-60",
                    "mph",
                    "kph",
                    "performance",
                    "sport",
                    "turbo",
                    "supercharged",
                    # EV specific terms
                    "electric",
                    "battery",
                    "charging",
                    "range",
                    "kwh",
                    "kw",
                    "fast",
                    "rapid",
                    "supercharging",
                    "dc",
                    "ac",
                    "volt",
                    "voltage",
                    "regenerative",
                    "regen",
                    "efficiency",
                    "mpge",
                    "miles",
                    "kilometers",
                    "charge",
                    "plug",
                    "outlet",
                    "station",
                    # Technology terms
                    "autopilot",
                    "autonomous",
                    "self-driving",
                    "adaptive",
                    "cruise",
                    "control",
                    "lane",
                    "assist",
                    "parking",
                    "sensors",
                    "camera",
                    "radar",
                    "lidar",
                    "navigation",
                    "gps",
                    "infotainment",
                    "touchscreen",
                    "display",
                    "connectivity",
                    "bluetooth",
                    "wifi",
                    "wireless",
                    "smartphone",
                    "app",
                    "over-the-air",
                    "ota",
                    "update",
                    "software",
                    # Safety terms
                    "airbag",
                    "airbags",
                    "safety",
                    "crash",
                    "test",
                    "rating",
                    "stars",
                    "iihs",
                    "nhtsa",
                    "collision",
                    "avoidance",
                    "emergency",
                    "braking",
                    "abs",
                    "stability",
                    "traction",
                    "control",
                    "blind",
                    "spot",
                    "monitoring",
                    # Comfort/luxury terms
                    "leather",
                    "heated",
                    "cooled",
                    "ventilated",
                    "seats",
                    "massage",
                    "memory",
                    "premium",
                    "luxury",
                    "comfort",
                    "climate",
                    "dual-zone",
                    "tri-zone",
                    "panoramic",
                    "sunroof",
                    "moonroof",
                    "ambient",
                    "lighting",
                    # Design terms
                    "aerodynamic",
                    "sleek",
                    "sporty",
                    "elegant",
                    "sophisticated",
                    "modern",
                    "futuristic",
                    "design",
                    "styling",
                    "exterior",
                    "interior",
                    "dashboard",
                    "cockpit",
                    "cabin",
                    "spacious",
                    "roomy",
                    "cargo",
                    "trunk",
                    "storage",
                    # Drivetrain terms
                    "awd",
                    "4wd",
                    "fwd",
                    "rwd",
                    "all-wheel",
                    "four-wheel",
                    "front-wheel",
                    "rear-wheel",
                    "drive",
                    "drivetrain",
                    "transmission",
                    "automatic",
                    "manual",
                    "cvt",
                    "dual-clutch",
                    "gearbox",
                    # Efficiency terms
                    "eco",
                    "green",
                    "sustainable",
                    "zero",
                    "emissions",
                    "clean",
                    "renewable",
                    "energy",
                    "efficient",
                    "economy",
                    # Warranty/service terms
                    "warranty",
                    "maintenance",
                    "service",
                    "certified",
                    "pre-owned",
                    "inspection",
                    "guarantee",
                    "coverage",
                    # Financing terms
                    "lease",
                    "financing",
                    "apr",
                    "down",
                    "payment",
                    "monthly",
                    "special",
                    "offer",
                    "deal",
                    "discount",
                    "rebate",
                    "incentive",
                }

                # Filter for automotive jargon only
                automotive_words = {
                    word: count
                    for word, count in word_freq.items()
                    if word in automotive_jargon and count > 1
                }

                # Get top automotive terms
                top_automotive_words = dict(
                    sorted(automotive_words.items(), key=lambda x: x[1], reverse=True)[
                        :20
                    ]
                )

                if top_automotive_words:
                    fig_words = px.bar(
                        x=list(top_automotive_words.values()),
                        y=list(top_automotive_words.keys()),
                        orientation="h",
                        title="Most Common Automotive Terms in Ad Titles",
                        color=list(top_automotive_words.values()),
                        color_continuous_scale="viridis",
                    )

                    # Add proper axis labels
                    fig_words.update_layout(
                        height=600,
                        xaxis_title="Number of Mentions",
                        yaxis_title="Automotive Terms",
                        showlegend=False,
                        margin=dict(l=20, r=20, t=60, b=40),
                    )

                    st.plotly_chart(fig_words, use_container_width=True)
                else:
                    st.info(
                        "No automotive jargon found in the current selection. Try expanding your filters."
                    )


if __name__ == "__main__":
    main()
