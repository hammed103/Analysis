#!/usr/bin/env python3
"""
Dataset Analysis Script for Merging Two Ad Datasets
This script analyzes both datasets to understand their structure and identify merge opportunities.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_dataset(file_path, dataset_name):
    """Analyze a single dataset and return key information."""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {dataset_name}")
    print(f"{'='*60}")
    
    try:
        # Read the dataset
        df = pd.read_csv(file_path, low_memory=False)
        
        print(f"Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"File Size: {Path(file_path).stat().st_size / (1024*1024):.1f} MB")
        
        # Column analysis
        print(f"\nColumn Information:")
        print(f"Total Columns: {len(df.columns)}")
        
        # Check for missing values
        missing_data = df.isnull().sum()
        columns_with_missing = missing_data[missing_data > 0]
        print(f"Columns with missing data: {len(columns_with_missing)}")
        
        # Data types
        print(f"\nData Types Distribution:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} columns")
        
        # Key columns analysis
        print(f"\nKey Columns Analysis:")
        
        # Look for ID columns
        id_columns = [col for col in df.columns if 'id' in col.lower()]
        print(f"ID-related columns: {id_columns}")
        
        # Look for advertiser columns
        advertiser_columns = [col for col in df.columns if 'advertiser' in col.lower()]
        print(f"Advertiser-related columns: {advertiser_columns}")
        
        # Look for date columns
        date_columns = [col for col in df.columns if any(word in col.lower() for word in ['date', 'shown', 'start', 'end', 'first', 'last'])]
        print(f"Date-related columns: {date_columns}")
        
        # Look for content columns
        content_columns = [col for col in df.columns if any(word in col.lower() for word in ['text', 'title', 'description', 'caption', 'summary'])]
        print(f"Content-related columns: {content_columns}")
        
        # Look for geographic columns
        geo_columns = [col for col in df.columns if any(word in col.lower() for word in ['region', 'country', 'countries', 'geographic'])]
        print(f"Geographic-related columns: {geo_columns}")
        
        # Look for impression/reach columns
        impression_columns = [col for col in df.columns if any(word in col.lower() for word in ['impression', 'reach', 'audience', 'spend'])]
        print(f"Impression/Reach-related columns: {impression_columns}")
        
        # Look for analysis columns
        analysis_columns = [col for col in df.columns if any(word in col.lower() for word in ['analysis', 'summary', 'openai', 'ocr'])]
        print(f"Analysis-related columns: {analysis_columns}")
        
        # Sample data for first few rows
        print(f"\nSample Data (first 3 rows):")
        print(df.head(3).to_string())
        
        return {
            'dataframe': df,
            'shape': df.shape,
            'columns': list(df.columns),
            'id_columns': id_columns,
            'advertiser_columns': advertiser_columns,
            'date_columns': date_columns,
            'content_columns': content_columns,
            'geo_columns': geo_columns,
            'impression_columns': impression_columns,
            'analysis_columns': analysis_columns,
            'missing_data': columns_with_missing
        }
        
    except Exception as e:
        print(f"Error analyzing {dataset_name}: {str(e)}")
        return None

def compare_datasets(dataset1_info, dataset2_info):
    """Compare two datasets and identify merge opportunities."""
    print(f"\n{'='*60}")
    print("DATASET COMPARISON & MERGE ANALYSIS")
    print(f"{'='*60}")
    
    # Size comparison
    print(f"Size Comparison:")
    print(f"  Dataset 1: {dataset1_info['shape'][0]:,} rows × {dataset1_info['shape'][1]} columns")
    print(f"  Dataset 2: {dataset2_info['shape'][0]:,} rows × {dataset2_info['shape'][1]} columns")
    
    # Column overlap analysis
    cols1 = set(dataset1_info['columns'])
    cols2 = set(dataset2_info['columns'])
    
    common_columns = cols1.intersection(cols2)
    unique_to_1 = cols1 - cols2
    unique_to_2 = cols2 - cols1
    
    print(f"\nColumn Analysis:")
    print(f"  Common columns: {len(common_columns)}")
    print(f"  Unique to Dataset 1: {len(unique_to_1)}")
    print(f"  Unique to Dataset 2: {len(unique_to_2)}")
    
    if common_columns:
        print(f"  Common columns: {sorted(list(common_columns))}")
    
    # Potential merge keys
    print(f"\nPotential Merge Strategies:")
    
    # Check for direct ID matches
    id_overlap = set(dataset1_info['id_columns']).intersection(set(dataset2_info['id_columns']))
    if id_overlap:
        print(f"  Direct ID matches possible: {list(id_overlap)}")
    
    # Check for advertiser matches
    adv_overlap = set(dataset1_info['advertiser_columns']).intersection(set(dataset2_info['advertiser_columns']))
    if adv_overlap:
        print(f"  Advertiser-based merge possible: {list(adv_overlap)}")
    
    # Suggest merge approach
    print(f"\nRecommended Merge Approach:")
    if 'advertiser_name' in common_columns:
        print("  ✓ Use 'advertiser_name' as primary merge key")
    elif adv_overlap:
        print(f"  ✓ Use advertiser columns: {list(adv_overlap)}")
    else:
        print("  ⚠ No direct merge key found - may need fuzzy matching on advertiser names")
    
    # Column mapping suggestions
    print(f"\nColumn Mapping Suggestions:")
    
    # Map similar columns
    column_mappings = {
        'advertiser': ['advertiser_name', 'advertiserName', 'page_name'],
        'content': ['ad_text', 'ad_title', 'shownAd/adTitle', 'shownAd/adDescription'],
        'dates': ['start_date', 'end_date', 'firstShown', 'lastShown'],
        'impressions': ['impressions_lower_bound', 'impressions_upper_bound'],
        'regions': ['region_code', 'region_name', 'targeted_countries']
    }
    
    for category, potential_cols in column_mappings.items():
        found_in_1 = [col for col in potential_cols if col in cols1]
        found_in_2 = [col for col in potential_cols if col in cols2]
        if found_in_1 or found_in_2:
            print(f"  {category.upper()}:")
            if found_in_1:
                print(f"    Dataset 1: {found_in_1}")
            if found_in_2:
                print(f"    Dataset 2: {found_in_2}")

def main():
    """Main analysis function."""
    print("DATASET MERGE ANALYSIS")
    print("=" * 60)
    
    # File paths
    dataset1_path = "Data/combined_with_analysis_2025-07-04_09-44-49.csv"
    dataset2_path = "Data/facebook_ads_electric_vehicles_with_openai_summaries_cached_with_countries_cleaned.csv"
    
    # Analyze both datasets
    dataset1_info = analyze_dataset(dataset1_path, "Google Ads Dataset (combined_with_analysis)")
    dataset2_info = analyze_dataset(dataset2_path, "Facebook Ads Dataset (facebook_ads_electric_vehicles)")
    
    if dataset1_info and dataset2_info:
        # Compare datasets
        compare_datasets(dataset1_info, dataset2_info)
        
        # Generate merge recommendations
        print(f"\n{'='*60}")
        print("MERGE RECOMMENDATIONS")
        print(f"{'='*60}")
        
        print("""
RECOMMENDED MERGE STRATEGY:

1. PRIMARY APPROACH - Advertiser-based Union:
   - Both datasets contain advertiser information
   - Combine datasets using UNION approach (stack vertically)
   - Add source column to identify origin dataset
   - Standardize column names for common fields

2. COLUMN STANDARDIZATION NEEDED:
   - Advertiser: 'advertiser_name' (FB) ↔ 'advertiserName' (Google)
   - Content: 'ad_text'/'ad_title' (FB) ↔ 'shownAd/adTitle'/'shownAd/adDescription' (Google)
   - Dates: 'start_date'/'end_date' (FB) ↔ 'firstShown'/'lastShown' (Google)
   - Impressions: Both have 'impressions_lower_bound'/'impressions_upper_bound'
   - Analysis: Both have OpenAI analysis fields

3. COLUMNS TO KEEP:
   - All unique analysis columns from both datasets
   - Standardized advertiser, content, date, and impression fields
   - Geographic information from both sources
   - Platform-specific metadata

4. COLUMNS TO CONSIDER DROPPING:
   - Redundant variation columns from Google dataset
   - Empty or mostly null columns
   - Platform-specific technical fields that don't add analytical value
        """)

if __name__ == "__main__":
    main()
