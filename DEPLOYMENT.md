# 🚀 Deployment Guide

This guide covers deploying the EV Advertisement Analysis Dashboard to various platforms.

## 📋 Pre-deployment Checklist

- [ ] All required files are present
- [ ] Data files are properly formatted
- [ ] Dependencies are listed in requirements.txt
- [ ] Dashboard runs locally without errors
- [ ] .gitignore excludes sensitive/large files

## 🌐 GitHub Setup

### 1. Create GitHub Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: EV Advertisement Analysis Dashboard"

# Add remote repository
git remote add origin https://github.com/yourusername/ev-advertisement-analysis.git

# Push to GitHub
git push -u origin main
```

### 2. Repository Structure
```
ev-advertisement-analysis/
├── .streamlit/
│   └── config.toml
├── ev_dashboard.py
├── data_processor.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── .gitignore
└── sample_data.csv (small sample for demo)
```

## ☁️ Streamlit Cloud Deployment

### 1. Prerequisites
- GitHub repository with your code
- Streamlit Cloud account (free)
- Data files accessible to the app

### 2. Deployment Steps

1. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

2. **Connect GitHub Account**
   - Sign in with GitHub
   - Authorize Streamlit Cloud

3. **Deploy New App**
   - Click "New app"
   - Select your repository
   - Choose branch (usually `main`)
   - Set main file path: `ev_dashboard.py`

4. **Configure Settings**
   - App URL: `your-app-name.streamlit.app`
   - Python version: 3.9+
   - Advanced settings (if needed)

5. **Deploy**
   - Click "Deploy!"
   - Wait for build to complete
   - App will be available at your custom URL

### 3. Data Handling for Cloud Deployment

**Option A: Small Sample Data**
```python
# Add to your repository
sample_data.csv  # Small subset for demo purposes
```

**Option B: External Data Source**
```python
# Modify ev_dashboard.py to load from URL
@st.cache_data
def load_data_from_url():
    url = "https://your-data-source.com/data.csv"
    return pd.read_csv(url)
```

**Option C: File Upload Widget**
```python
# Add file upload option
uploaded_file = st.file_uploader("Upload your CSV data", type="csv")
if uploaded_file:
    analyzer = EVAdvertAnalyzer(uploaded_file)
```

## 🐳 Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "ev_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Build and Run
```bash
# Build image
docker build -t ev-dashboard .

# Run container
docker run -p 8501:8501 ev-dashboard
```

## 🔧 Environment Variables

For sensitive configuration, use environment variables:

```python
import os

# In your code
DATA_URL = os.getenv('DATA_URL', 'default_local_path.csv')
API_KEY = os.getenv('API_KEY', '')
```

Set in Streamlit Cloud:
- Go to app settings
- Add secrets in `secrets.toml` format

## 📊 Performance Optimization

### 1. Caching
```python
@st.cache_data
def load_data():
    # Expensive data loading
    pass

@st.cache_resource
def create_analyzer():
    # Resource-intensive object creation
    pass
```

### 2. Data Size Management
- Use data sampling for large datasets
- Implement pagination for large results
- Consider data compression

### 3. Memory Management
```python
# Clear cache when needed
st.cache_data.clear()

# Monitor memory usage
import psutil
memory_usage = psutil.virtual_memory().percent
```

## 🔒 Security Considerations

### 1. Data Privacy
- Remove sensitive information from public repos
- Use environment variables for credentials
- Implement access controls if needed

### 2. Input Validation
```python
# Validate uploaded files
if uploaded_file:
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("File too large")
        return
```

## 🚀 Alternative Deployment Options

### 1. Heroku
- Create `Procfile`: `web: streamlit run ev_dashboard.py --server.port=$PORT`
- Add `setup.sh` for configuration
- Deploy via Git or GitHub integration

### 2. AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Set up load balancing for high traffic
- Configure auto-scaling

### 3. Self-hosted
- Use reverse proxy (nginx)
- Set up SSL certificates
- Configure monitoring and logging

## 📈 Monitoring and Maintenance

### 1. Health Checks
```python
# Add health check endpoint
if st.sidebar.button("Health Check"):
    st.success("Dashboard is running normally")
    st.info(f"Data loaded: {len(analyzer.df)} records")
```

### 2. Error Handling
```python
try:
    analyzer = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()
```

### 3. Usage Analytics
- Monitor app performance
- Track user interactions
- Analyze error logs

## 🔄 Updates and Versioning

### 1. Continuous Deployment
- Set up GitHub Actions for auto-deployment
- Use branch protection rules
- Implement staging environment

### 2. Version Management
```python
# Add version info to app
__version__ = "1.0.0"
st.sidebar.text(f"Version: {__version__}")
```

## 📞 Support and Troubleshooting

### Common Issues
1. **Memory errors**: Reduce data size or optimize caching
2. **Slow loading**: Implement data pagination
3. **Deployment failures**: Check requirements.txt and Python version
4. **Data access**: Verify file paths and permissions

### Getting Help
- Streamlit Community Forum
- GitHub Issues
- Documentation: https://docs.streamlit.io/

---

**Ready to deploy your EV Advertisement Analysis Dashboard!** 🚗📊
