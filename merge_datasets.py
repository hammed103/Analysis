#!/usr/bin/env python3
"""
Dataset Merger Script
Merges Google Ads and Facebook Ads datasets for electric vehicle advertising analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


def load_and_clean_google_data(file_path):
    """Load and clean Google Ads dataset."""
    print("Loading Google Ads dataset...")
    df = pd.read_csv(file_path, low_memory=False)
    print(f"Original Google dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # Select core columns for merge
    google_columns = {
        "advertiserName": "advertiser_name",
        "shownAd/adTitle": "ad_title",
        "shownAd/adDescription": "ad_description",
        "firstShown": "start_date",
        "lastShown": "end_date",
        "impressions_lower_bound": "impressions_lower",
        "impressions_upper_bound": "impressions_upper",
        "region_name": "region_info",
        "openai_analysis": "openai_analysis",
        "archiveImageUrl": "image_url",
        "ocr_text": "ocr_text",
        "advertiserDomain": "advertiser_domain",
        "creativeId": "creative_id",
        "region_code": "region_code",
        "platform": "platform_type",
    }

    # Select available columns
    available_cols = [col for col in google_columns.keys() if col in df.columns]
    google_clean = df[available_cols].copy()

    # Rename columns
    google_clean = google_clean.rename(
        columns={col: google_columns[col] for col in available_cols}
    )

    # Add source identifier
    google_clean["source_platform"] = "google"

    # Clean data types
    if "start_date" in google_clean.columns:
        google_clean["start_date"] = pd.to_datetime(
            google_clean["start_date"], errors="coerce"
        )
    if "end_date" in google_clean.columns:
        google_clean["end_date"] = pd.to_datetime(
            google_clean["end_date"], errors="coerce"
        )

    print(
        f"Cleaned Google dataset: {google_clean.shape[0]:,} rows × {google_clean.shape[1]} columns"
    )
    return google_clean


def load_and_clean_facebook_data(file_path):
    """Load and clean Facebook Ads dataset."""
    print("Loading Facebook Ads dataset...")
    df = pd.read_csv(file_path, low_memory=False)
    print(f"Original Facebook dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # Select core columns for merge
    facebook_columns = {
        "advertiser_name": "advertiser_name",
        "page_name": "page_name",
        "ad_title": "ad_title",
        "ad_text": "ad_description",
        "start_date": "start_date",
        "end_date": "end_date",
        "impressions_lower_bound": "impressions_lower",
        "impressions_upper_bound": "impressions_upper",
        "targeted_countries": "region_info",
        "targeted_countries_list": "targeted_countries_list",
        "openai_summary": "openai_analysis",
        "first_image_url": "image_url",
        "spend": "spend",
        "reach_estimate": "reach_estimate",
        "page_like_count": "page_like_count",
        "ad_archive_id": "ad_archive_id",
        "cta_text": "cta_text",
        "matched_car_models": "matched_car_models",
    }

    # Select available columns
    available_cols = [col for col in facebook_columns.keys() if col in df.columns]
    facebook_clean = df[available_cols].copy()

    # Rename columns
    facebook_clean = facebook_clean.rename(
        columns={col: facebook_columns[col] for col in available_cols}
    )

    # Add source identifier
    facebook_clean["source_platform"] = "facebook"

    # Clean data types
    if "start_date" in facebook_clean.columns:
        facebook_clean["start_date"] = pd.to_datetime(
            facebook_clean["start_date"], errors="coerce"
        )
    if "end_date" in facebook_clean.columns:
        facebook_clean["end_date"] = pd.to_datetime(
            facebook_clean["end_date"], errors="coerce"
        )

    # Handle advertiser_name - use page_name if advertiser_name is null
    if (
        "advertiser_name" in facebook_clean.columns
        and "page_name" in facebook_clean.columns
    ):
        facebook_clean["advertiser_name"] = facebook_clean["advertiser_name"].fillna(
            facebook_clean["page_name"]
        )

    print(
        f"Cleaned Facebook dataset: {facebook_clean.shape[0]:,} rows × {facebook_clean.shape[1]} columns"
    )
    return facebook_clean


def merge_datasets(google_df, facebook_df):
    """Merge the two cleaned datasets."""
    print("\nMerging datasets...")

    # Get all unique columns from both datasets
    all_columns = set(google_df.columns) | set(facebook_df.columns)

    # Ensure both dataframes have all columns (fill missing with NaN)
    for col in all_columns:
        if col not in google_df.columns:
            google_df[col] = np.nan
        if col not in facebook_df.columns:
            facebook_df[col] = np.nan

    # Reorder columns to match
    column_order = sorted(all_columns)
    google_df = google_df[column_order]
    facebook_df = facebook_df[column_order]

    # Concatenate datasets
    merged_df = pd.concat([google_df, facebook_df], ignore_index=True, sort=False)

    print(f"Merged dataset: {merged_df.shape[0]:,} rows × {merged_df.shape[1]} columns")
    return merged_df


def generate_summary_report(merged_df):
    """Generate a summary report of the merged dataset."""
    print("\n" + "=" * 60)
    print("MERGED DATASET SUMMARY REPORT")
    print("=" * 60)

    # Basic statistics
    print(f"Total Records: {merged_df.shape[0]:,}")
    print(f"Total Columns: {merged_df.shape[1]}")

    # Platform distribution
    platform_counts = merged_df["source_platform"].value_counts()
    print(f"\nPlatform Distribution:")
    for platform, count in platform_counts.items():
        percentage = (count / len(merged_df)) * 100
        print(f"  {platform.title()}: {count:,} ({percentage:.1f}%)")

    # Date range
    if "start_date" in merged_df.columns:
        start_dates = pd.to_datetime(merged_df["start_date"], errors="coerce")
        min_date = start_dates.min()
        max_date = start_dates.max()
        print(
            f"\nDate Range: {min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else 'N/A'} to {max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else 'N/A'}"
        )

    # Top advertisers
    if "advertiser_name" in merged_df.columns:
        top_advertisers = merged_df["advertiser_name"].value_counts().head(10)
        print(f"\nTop 10 Advertisers:")
        for advertiser, count in top_advertisers.items():
            if pd.notna(advertiser):
                print(f"  {advertiser}: {count:,} ads")

    # Data completeness
    print(f"\nData Completeness (non-null values):")
    completeness = ((merged_df.notna().sum() / len(merged_df)) * 100).sort_values(
        ascending=False
    )
    for col, percentage in completeness.head(10).items():
        print(f"  {col}: {percentage:.1f}%")

    # Analysis availability
    if "openai_analysis" in merged_df.columns:
        analysis_available = merged_df["openai_analysis"].notna().sum()
        analysis_percentage = (analysis_available / len(merged_df)) * 100
        print(
            f"\nOpenAI Analysis Available: {analysis_available:,} records ({analysis_percentage:.1f}%)"
        )


def main():
    """Main execution function."""
    print("ELECTRIC VEHICLE ADS DATASET MERGER")
    print("=" * 50)

    # File paths
    google_file = "Data/combined_with_analysis_2025-07-04_09-44-49.csv"
    facebook_file = "Data/facebook_ads_electric_vehicles_with_openai_summaries_cached_with_countries_cleaned.csv"

    try:
        # Load and clean datasets
        google_clean = load_and_clean_google_data(google_file)
        facebook_clean = load_and_clean_facebook_data(facebook_file)

        # Merge datasets
        merged_dataset = merge_datasets(google_clean, facebook_clean)

        # Generate summary report
        generate_summary_report(merged_dataset)

        # Save merged dataset
        output_file = (
            f"Data/merged_ev_ads_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        print(f"\nSaving merged dataset to: {output_file}")
        merged_dataset.to_csv(output_file, index=False)
        print("✓ Merge completed successfully!")

        # Save column mapping for reference
        mapping_file = (
            f"Data/column_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(mapping_file, "w") as f:
            f.write("MERGED DATASET COLUMN MAPPING\n")
            f.write("=" * 40 + "\n\n")
            f.write("Columns in merged dataset:\n")
            for i, col in enumerate(sorted(merged_dataset.columns), 1):
                f.write(f"{i:2d}. {col}\n")

        print(f"✓ Column mapping saved to: {mapping_file}")

        return merged_dataset

    except Exception as e:
        print(f"Error during merge process: {str(e)}")
        return None


if __name__ == "__main__":
    merged_data = main()
