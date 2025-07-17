# EV Advertisement Analysis Dashboard

## Overview
A comprehensive Streamlit dashboard for analyzing electric vehicle advertisements across Portugal, Germany, and Netherlands markets. The dashboard leverages the updated `data_processor.py` that uses:
- **`country`** column for market filtering
- **`matched_cars`** column for vehicle identification  
- **`openai_analysis`** column for feature extraction

## Features

### 📊 Market Overview
- **Market Distribution**: Bar chart showing advertisement volume by country
- **Vehicle Share**: Pie chart displaying market share by vehicle model
- **Key Metrics**: Total ads, unique vehicles, advertisers, and date range

### 🔧 Feature Analysis
- **Top Features**: Horizontal bar chart of most mentioned feature categories
- **Feature Heatmap**: Cross-vehicle feature comparison matrix
- **Detailed Mentions**: Expandable sections with actual feature content from ads

### 🌍 Market vs Vehicle Analysis
- **Stacked Bar Chart**: Shows how each vehicle performs in different markets
- **Market Breakdown**: Detailed analysis of vehicle distribution across countries

### 📈 Time Series Analysis
- **Trend Analysis**: Line chart showing advertisement volume over time
- **Filtering**: Can be filtered by market and/or vehicle model

### 💾 Data Export
- **Market Summary**: Export market statistics as CSV
- **Feature Analysis**: Export feature mention counts as CSV
- **Market-Vehicle Matrix**: Export cross-analysis data as CSV

## Installation & Setup

### Prerequisites
```bash
pip3 install streamlit plotly pandas
```

### Data Requirements
The dashboard expects one of these CSV files to exist:
- `work.csv` (preferred - created from the notebook analysis)
- `Data/merged_ev_ads_dataset_20250716_171722.csv`
- `Data/merged_ev_ads_dataset_20250716_170109.csv`

### Required Columns
The CSV file should contain:
- `country`: Market information (Portugal, Germany, Netherlands)
- `matched_cars`: Vehicle model names
- `openai_analysis`: AI-generated feature analysis
- `start_date`: Advertisement start dates
- `page_name`: Advertiser information
- `vehicle_model`: Vehicle model (fallback for matched_cars)

## Running the Dashboard

### Command Line
```bash
python3 -m streamlit run ev_dashboard.py
```

### Access
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.1.253:8501 (for network access)

## Dashboard Sections

### 1. Sidebar Filters
- **Market Filter**: Select specific country or "All"
- **Vehicle Filter**: Select specific vehicle model or "All"

### 2. Key Metrics (Top Row)
- Total advertisement count
- Number of unique vehicles
- Number of unique advertisers  
- Date range of the dataset

### 3. Market Overview
- **Left**: Market distribution bar chart
- **Right**: Vehicle share pie chart

### 4. Feature Analysis
- **Left**: Top mentioned features (filtered by selection)
- **Right**: Feature heatmap (when "All" vehicles selected) or feature details (when specific vehicle selected)

### 5. Detailed Analysis
- **Feature Mentions Button**: Shows expandable sections with actual ad content
- Displays advertiser, platform, and relevant text for each mention

### 6. Market vs Vehicle Analysis
- Stacked bar chart showing vehicle performance across markets
- Helps identify which vehicles are popular in which countries

### 7. Time Series Analysis
- Line chart showing advertisement trends over time
- Respects current filter selections

### 8. Data Export
- Three export options for different analysis needs
- All exports are in CSV format for further analysis

## Data Processing

The dashboard uses the updated `EVAdvertAnalyzer` class which:

1. **Prioritizes new column structure**:
   - Uses `country` over `targeted_countries_list`
   - Uses `matched_cars` over `matched_car_models`
   - Uses `openai_analysis` over `openai_summary`

2. **Filters for target data**:
   - Markets: Portugal, Germany, Netherlands
   - Vehicles: Hyundai Ioniq 5, VW ID.4, Renault Megane E-Tech, Audi Q4 e-tron, Tesla Model Y

3. **Extracts structured features**:
   - Parses **Section:** format from OpenAI analysis
   - Categorizes features into meaningful groups
   - Filters out low-quality content

## Performance Notes

- Data is cached using `@st.cache_data` for faster loading
- Large datasets may take a few seconds to process initially
- Time series analysis may show timezone warnings (cosmetic only)

## Troubleshooting

### Common Issues
1. **"No data file found"**: Ensure one of the expected CSV files exists
2. **Empty charts**: Check if data matches the expected column structure
3. **Slow loading**: Large datasets may take time to process initially

### Data Validation
The dashboard will show:
- Total records loaded
- Records after filtering
- Available columns in the sidebar

## Example Usage

1. **Market Comparison**: Set filters to "All" to see overall market distribution
2. **Vehicle Focus**: Select specific vehicle to see its feature profile
3. **Country Analysis**: Filter by country to see local market characteristics
4. **Trend Analysis**: Use time series to identify seasonal patterns
5. **Export Data**: Download specific analysis results for presentations

## Technical Details

- **Framework**: Streamlit 1.46.0+
- **Visualization**: Plotly Express
- **Data Processing**: Pandas
- **Caching**: Streamlit native caching
- **Export Format**: CSV

The dashboard provides a comprehensive view of EV advertisement strategies across European markets, enabling competitive analysis and market insights.
