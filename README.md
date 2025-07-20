# 🚗 EV Advertisement Analysis Dashboard

A comprehensive Streamlit dashboard for analyzing electric vehicle advertisements across Portugal, Germany, and Netherlands markets.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see requirements.txt)

### Installation & Run

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the dashboard**:
```bash
python3 -m streamlit run fixed_enhanced_dashboard.py
```

3. **Open your browser** to `http://localhost:8502`

## 📊 Dashboard Features

### 🎛️ **Smart Filtering**
- **Market Filter**: Portugal, Germany, Netherlands
- **Vehicle Filter**: Focus on specific EV models
- **Real-time Updates**: All charts update instantly

### 📈 **Analysis Tabs**

#### **📊 Overview Tab**
- Key metrics (total ads, unique vehicles, advertisers)
- Market distribution charts
- Vehicle market share analysis
- Feature analysis with top mentions
- Market vs Vehicle cross-analysis
- Time series trends
- Data export options

#### **🔍 Feature Analysis Tab**
- Detailed feature breakdowns by category
- Quality content filtering (removes "not specified")
- Advertiser and platform context
- Expandable sections with full mention details

### ⚡ **Performance Features**
- **Cached data loading** for instant filter responses
- **Smart processing** optimized for large datasets
- **Synchronized filtering** across all visualizations

## 📁 **Data Sources**

The dashboard loads from:
- `ev_ads_complete_with_images_and_gender_20250720_100525.csv` - **Main Dataset** (21MB)
- `ev_ad_images/` - Image assets and metadata

### Dataset Contains:
- **211,851 total ads** with 11,090 target vehicle ads
- **Markets**: Portugal, Germany, Netherlands
- **Vehicles**: Hyundai Ioniq 5, VW ID.4, Tesla Model Y, Audi Q4 e-tron, BMW iX1/iX3
- **Analysis**: OpenAI feature analysis, gender targeting, image URLs
- **Advertisers**: Official brands and dealers

## 🎯 **Key Insights**

The dashboard reveals insights like:
- **Hyundai Ioniq 5** leads with 4,529 ads (41% of target vehicles)
- **VW ID.4** strong presence with 3,508 ads (32% of target vehicles)
- **Portugal market** dominates with 6,749 ads (61% of target markets)
- **Range & Charging** most advertised feature category
- **Gender targeting** patterns reveal audience strategies

## 🔧 **Technical Stack**

- **Frontend**: Streamlit
- **Data Processing**: Pandas + NumPy
- **Visualization**: Plotly
- **Caching**: Streamlit cache optimization

## 📈 **Analysis Capabilities**

- **Market Analysis**: Volume, share, geographic trends
- **Vehicle Analysis**: Model performance, competitive positioning
- **Feature Analysis**: AI-powered content insights
- **Temporal Analysis**: Trends, seasonality, campaign timing

## 🚀 **Deployment**

Works on:
- Local development (`streamlit run ev_dashboard.py`)
- Streamlit Cloud
- Heroku, AWS, GCP, Azure

---

*Built for comprehensive EV market intelligence* 🔋
