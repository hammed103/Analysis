# 🚗 EV Advertisement Analysis Dashboard

A comprehensive Streamlit dashboard for analyzing electric vehicle advertisements across **Portugal**, **Germany**, and **Netherlands** markets. Features advanced filtering, duplicate removal, and detailed feature analysis with actual advertisement content.

## 🚀 Live Demo

**Dashboard URL**: [Deploy on Streamlit Cloud](https://share.streamlit.io/)

## 📋 Features

### 📊 Overview Tab
- **Market Distribution**: Advertisement volume by country with interactive charts
- **Vehicle Share**: Market share analysis by vehicle model
- **Feature Analysis**: Top mentioned features with filtering and heatmaps
- **Market vs Vehicle Analysis**: Cross-analysis of vehicle performance by country
- **Time Series Analysis**: Advertisement trends over time
- **Data Export**: CSV export functionality for all analyses

### 🔍 Detailed Feature Analysis Tab
- **Interactive Feature Exploration**: Click on any feature category to see actual mentions
- **Smart Content Filtering**: Automatically removes "not specified" and low-quality content
- **Advanced Filtering**: Removes variations like "not discussed in the ad", "not mentioned", etc.
- **Duplicate Removal**: Shows only unique mentions to avoid repetition
- **Flexible Display**: Option to show first 50 or all unique mentions
- **Rich Context**: Shows advertiser, platform, section, and full content for each mention

### 🎯 Target Analysis
- **Markets**: Portugal, Germany, Netherlands
- **Vehicles**: Hyundai Ioniq 5, VW ID.4, Renault Megane E-Tech, Audi Q4 e-tron, Tesla Model Y
- **Features**: Brand Focus, Design, Technology, Safety, Interior, Performance, Range & Charging

### 🔍 Interactive Features
- **Dual-tab Interface**: Overview and detailed feature analysis
- **Market & Vehicle Filtering**: Real-time filtering across all visualizations
- **Smart Content Processing**: AI-powered feature extraction and categorization
- **Export Functionality**: Download analysis results in CSV format

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- One of these data files:
  - `work.csv` (preferred - processed dataset)
  - `Data/merged_ev_ads_dataset_20250716_171722.csv`
  - `Data/merged_ev_ads_dataset_20250716_170109.csv`

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ev-advertisement-analysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your data file** (one of the supported formats above)

4. **Run the dashboard**:
   ```bash
   streamlit run ev_dashboard.py
   ```

5. **Open your browser** to `http://localhost:8501`

### Required CSV Columns
Your data file should contain:
- `country`: Market information (Portugal, Germany, Netherlands)
- `matched_cars`: Vehicle model names
- `openai_analysis`: AI-generated feature analysis
- `start_date`: Advertisement start dates
- `page_name`: Advertiser information
- `vehicle_model`: Vehicle model (fallback for matched_cars)

## 📊 Dashboard Interface

### Tab 1: 📊 Overview
- **Key Metrics**: Total ads, unique vehicles, advertisers, date range
- **Market Distribution**: Bar chart showing advertisement volume by country
- **Vehicle Share**: Pie chart displaying market share by vehicle model
- **Feature Analysis**: Top mentioned features with interactive filtering
- **Feature Heatmap**: Cross-vehicle feature comparison matrix
- **Market vs Vehicle Analysis**: Stacked bar chart of vehicle performance by country
- **Time Series Analysis**: Advertisement trends over time with filtering
- **Data Export**: Market summary, feature analysis, and market-vehicle matrix

### Tab 2: 🔍 Detailed Feature Analysis
- **Vehicle Selection**: Choose specific vehicle or view all
- **Feature Categories**: Expandable sections for each feature type
- **Smart Filtering**: Removes "not specified", "not discussed" content
- **Duplicate Removal**: Shows only unique mentions
- **Rich Context**: Advertiser, platform, section, and full content
- **Flexible Display**: Show first 50 or all unique mentions
- **Quality Metrics**: Shows filtered vs total mention counts

## 📁 Project Structure

```
├── ev_dashboard.py             # Main dashboard application
├── data_processor.py           # Advanced data processing engine
├── test_data_processor.py      # Testing script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── DASHBOARD_README.md         # Detailed dashboard documentation
└── Data/                       # Data directory
    ├── work.csv                # Processed dataset (preferred)
    └── merged_ev_ads_dataset_*.csv  # Alternative datasets
```

## 🎨 Key Insights Provided

### Vehicle Features Analysis
- **Range & Performance**: Battery life, acceleration, power metrics
- **Interior & Comfort**: Seating, spaciousness, cabin features
- **Technology**: Infotainment, connectivity, smart features
- **Safety**: Protection systems, driver assistance
- **Design**: Aesthetic appeal, styling elements
- **Eco-Friendliness**: Environmental benefits, sustainability

### Image Theme Categories
- **Setting**: Urban vs rural environments
- **Focus**: Interior vs exterior emphasis
- **Purpose**: Lifestyle vs commuting orientation
- **Style**: Luxury vs sport positioning

### Style & Tone Analysis
- **Modern**: Contemporary, current, latest
- **Innovative**: Cutting-edge, advanced, revolutionary
- **Elegant**: Sophisticated, refined, classy
- **Energetic**: Dynamic, vibrant, exciting
- **Minimalist**: Clean, simple, sleek
- **Professional**: Business, corporate, formal
- **Friendly**: Approachable, welcoming, warm

## 🔧 Technical Details

### Data Processing
- Filters advertisements targeting Portugal, Germany, Netherlands
- Processes OpenAI summaries for feature extraction
- Analyzes image themes and messaging tone
- Aggregates statistics across markets and vehicles

### Visualization
- Interactive Plotly charts and graphs
- Responsive design for different screen sizes
- Color-coded analysis for easy interpretation
- Export capabilities for further analysis

## 📈 Use Cases

1. **Competitive Intelligence**: Understand competitor messaging strategies
2. **Market Analysis**: Compare advertising approaches across markets
3. **Feature Positioning**: Analyze how features are communicated
4. **Brand Positioning**: Study tone and style differences
5. **Campaign Planning**: Inform future advertising strategies

## 🤝 Support

For questions or issues:
1. Check that all required files are in place
2. Ensure Python dependencies are installed
3. Verify the data file path is correct
4. Review the console output for error messages

## 📄 License

This project is for internal analysis purposes. Please ensure compliance with data usage policies and regulations.
# Analysis
