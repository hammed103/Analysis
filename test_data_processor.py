#!/usr/bin/env python3
"""
Test script to verify the updated data_processor.py works with the new column structure
"""

import pandas as pd
import sys
import os
from data_processor import EVAdvertAnalyzer

def test_data_processor():
    """Test the updated data processor with the new column structure"""
    
    # Look for the work.csv file that was created in the notebook
    csv_files = [
        "work.csv",
        "Data/merged_ev_ads_dataset_20250716_171722.csv",
        "Data/merged_ev_ads_dataset_20250716_170109.csv"
    ]
    
    csv_path = None
    for file_path in csv_files:
        if os.path.exists(file_path):
            csv_path = file_path
            print(f"Found data file: {csv_path}")
            break
    
    if not csv_path:
        print("No data file found. Please ensure one of these files exists:")
        for file_path in csv_files:
            print(f"  - {file_path}")
        return False
    
    try:
        # Test loading the data
        print("\n1. Testing data loading...")
        analyzer = EVAdvertAnalyzer(csv_path)
        
        print(f"   ✓ Loaded {len(analyzer.df)} total records")
        print(f"   ✓ Filtered to {len(analyzer.df_filtered)} target records")
        
        # Check available columns
        print("\n2. Checking available columns...")
        available_columns = list(analyzer.df.columns)
        print(f"   Total columns: {len(available_columns)}")
        
        # Check for key columns
        key_columns = ["country", "matched_cars", "openai_analysis"]
        for col in key_columns:
            if col in available_columns:
                print(f"   ✓ {col} column found")
            else:
                print(f"   ⚠ {col} column not found")
        
        # Test market summary
        print("\n3. Testing market summary...")
        market_summary = analyzer.get_market_summary()
        for market, stats in market_summary.items():
            print(f"   {market}: {stats['total_ads']} ads, {stats['unique_vehicles']} vehicles")
        
        # Test vehicle analysis
        print("\n4. Testing vehicle analysis...")
        vehicle_analysis = analyzer.get_vehicle_analysis()
        for vehicle, stats in list(vehicle_analysis.items())[:3]:  # Show first 3
            print(f"   {vehicle}: {stats['total_ads']} ads")
        
        # Test feature analysis
        print("\n5. Testing feature analysis...")
        feature_analysis = analyzer.analyze_features_mentioned()
        for vehicle, features in list(feature_analysis.items())[:2]:  # Show first 2
            print(f"   {vehicle}:")
            for feature, count in list(features.items())[:3]:  # Show first 3 features
                print(f"     - {feature}: {count}")
        
        print("\n✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_processor()
    sys.exit(0 if success else 1)
