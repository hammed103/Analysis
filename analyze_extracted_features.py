#!/usr/bin/env python3
"""
Script to analyze the extracted features and create detailed insights.
"""

import pandas as pd
import json
import ast
from collections import defaultdict, Counter

def safe_eval(x):
    """Safely evaluate string representations of dictionaries"""
    if pd.isna(x) or x == '{}':
        return {}
    try:
        return ast.literal_eval(x)
    except:
        return {}

def analyze_features():
    """Analyze the extracted features in detail"""
    
    # Load the extracted features
    df = pd.read_csv('extracted_features.csv')
    print(f"Analyzing {len(df)} ads...")
    
    # Convert string representations back to dictionaries
    df['features'] = df['features'].apply(safe_eval)
    df['image_content'] = df['image_content'].apply(safe_eval)
    df['themes'] = df['themes'].apply(safe_eval)
    
    # Analysis by car model and market
    results = {}
    
    for car_model in df['car_model'].unique():
        if pd.isna(car_model):
            continue
            
        results[car_model] = {}
        car_data = df[df['car_model'] == car_model]
        
        for market in car_data['market'].unique():
            if pd.isna(market):
                continue
                
            market_data = car_data[car_data['market'] == market]
            
            # Feature analysis
            feature_counts = defaultdict(int)
            feature_details = defaultdict(list)
            
            for _, row in market_data.iterrows():
                features = row['features']
                for category, feature_list in features.items():
                    feature_counts[category] += len(feature_list)
                    for feature in feature_list:
                        feature_details[category].append(feature['section'])
            
            # Image content analysis
            image_counts = defaultdict(int)
            for _, row in market_data.iterrows():
                image_content = row['image_content']
                for img_type, present in image_content.items():
                    if present:
                        image_counts[img_type] += 1
            
            # Theme analysis
            theme_analysis = defaultdict(list)
            for _, row in market_data.iterrows():
                themes = row['themes']
                for theme_type, content in themes.items():
                    if content:
                        theme_analysis[theme_type].append(content)
            
            results[car_model][market] = {
                'total_ads': len(market_data),
                'feature_counts': dict(feature_counts),
                'feature_details': dict(feature_details),
                'image_counts': dict(image_counts),
                'theme_analysis': dict(theme_analysis)
            }
    
    return results

def create_detailed_report(results):
    """Create a detailed report of the analysis"""
    
    report = []
    report.append("# EV Advertisement Analysis Report")
    report.append("## Based on matched_cars and country columns with features extracted from openai_analysis")
    report.append("")
    
    for car_model, markets in results.items():
        report.append(f"## {car_model}")
        report.append("")
        
        for market, data in markets.items():
            report.append(f"### {market} Market")
            report.append(f"- **Total Ads**: {data['total_ads']}")
            report.append("")
            
            # Feature analysis
            if data['feature_counts']:
                report.append("#### Feature Categories Mentioned:")
                for category, count in sorted(data['feature_counts'].items(), key=lambda x: x[1], reverse=True):
                    report.append(f"- **{category}**: {count} mentions")
                report.append("")
            
            # Image content analysis
            if data['image_counts']:
                report.append("#### Image Content Types:")
                for img_type, count in sorted(data['image_counts'].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / data['total_ads']) * 100
                    report.append(f"- **{img_type.title()}**: {count} ads ({percentage:.1f}%)")
                report.append("")
            
            # Most common feature sections
            if data['feature_details']:
                report.append("#### Most Common Feature Sections:")
                all_sections = []
                for category, sections in data['feature_details'].items():
                    all_sections.extend(sections)
                
                section_counts = Counter(all_sections)
                for section, count in section_counts.most_common(5):
                    report.append(f"- **{section}**: {count} times")
                report.append("")
            
            report.append("---")
            report.append("")
    
    return "\n".join(report)

def create_comparison_table():
    """Create a comparison table across cars and markets"""
    
    # Load the feature summary
    summary_df = pd.read_csv('feature_summary.csv')
    
    # Fill NaN values with 0
    summary_df = summary_df.fillna(0)
    
    # Create pivot tables for different analyses
    feature_columns = [col for col in summary_df.columns if col.startswith('feature_')]
    
    comparison_data = []
    
    for _, row in summary_df.iterrows():
        car = row['car_model']
        market = row['market']
        
        # Calculate total feature mentions
        total_features = sum(row[col] for col in feature_columns)
        
        # Get top feature categories
        feature_scores = {col.replace('feature_', ''): row[col] for col in feature_columns}
        top_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        comparison_data.append({
            'Car Model': car,
            'Market': market,
            'Total Feature Mentions': int(total_features),
            'Top Feature 1': f"{top_features[0][0]} ({int(top_features[0][1])})" if top_features else "",
            'Top Feature 2': f"{top_features[1][0]} ({int(top_features[1][1])})" if len(top_features) > 1 else "",
            'Top Feature 3': f"{top_features[2][0]} ({int(top_features[2][1])})" if len(top_features) > 2 else "",
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    return comparison_df

def main():
    print("Analyzing extracted features...")
    
    # Perform detailed analysis
    results = analyze_features()
    
    # Create detailed report
    report = create_detailed_report(results)
    
    # Save the report
    with open('feature_analysis_report.md', 'w') as f:
        f.write(report)
    print("Saved detailed report to feature_analysis_report.md")
    
    # Create comparison table
    comparison_df = create_comparison_table()
    comparison_df.to_csv('feature_comparison.csv', index=False)
    print("Saved feature comparison to feature_comparison.csv")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Analyzed {len(comparison_df)} car-market combinations")
    print("\nTop performing combinations by total feature mentions:")
    top_combinations = comparison_df.nlargest(5, 'Total Feature Mentions')
    for _, row in top_combinations.iterrows():
        print(f"- {row['Car Model']} in {row['Market']}: {row['Total Feature Mentions']} features")
    
    print("\nAnalysis complete! Check the following files:")
    print("- feature_analysis_report.md: Detailed analysis report")
    print("- feature_comparison.csv: Comparison table")
    print("- extracted_features.csv: Raw extracted features")
    print("- feature_summary.csv: Aggregated feature counts")

if __name__ == "__main__":
    main()
