#!/bin/bash

# EV Advertisement Analysis Dashboard - Deployment Script
# This script helps deploy the dashboard to GitHub and Streamlit Cloud

set -e  # Exit on any error

echo "🚗 EV Advertisement Analysis Dashboard - Deployment Script"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

print_status "Environment checks passed"

# Check if this is already a git repository
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    print_status "Git repository initialized"
else
    print_info "Git repository already exists"
fi

# Install dependencies and test
print_info "Installing dependencies..."
pip3 install -r requirements.txt

print_info "Testing data processor..."
python3 -c "
from data_processor import EVAdvertAnalyzer
import os

# Test with sample data
if os.path.exists('sample_data.csv'):
    try:
        analyzer = EVAdvertAnalyzer('sample_data.csv')
        print('✅ Data processor test passed')
        print(f'Loaded {len(analyzer.df)} records')
        print(f'Filtered to {len(analyzer.df_filtered)} target records')
    except Exception as e:
        print(f'❌ Data processor test failed: {e}')
        exit(1)
else:
    print('⚠️  No sample data found, skipping data processor test')
"

print_status "Dependencies installed and tested"

# Check for required files
required_files=("ev_dashboard.py" "data_processor.py" "requirements.txt" "README.md")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_status "All required files present"

# Add files to git
print_info "Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    print_warning "No changes to commit"
else
    # Commit changes
    echo "Enter commit message (or press Enter for default):"
    read -r commit_message
    if [ -z "$commit_message" ]; then
        commit_message="Deploy EV Advertisement Analysis Dashboard"
    fi
    
    git commit -m "$commit_message"
    print_status "Changes committed"
fi

# Check if remote origin exists
if git remote get-url origin &> /dev/null; then
    print_info "Remote origin already configured"
    
    # Ask if user wants to push
    echo "Do you want to push to GitHub? (y/n):"
    read -r push_confirm
    if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
        print_info "Pushing to GitHub..."
        git push origin main
        print_status "Pushed to GitHub successfully"
    fi
else
    print_warning "No remote origin configured"
    echo "Please add your GitHub repository URL:"
    echo "Example: https://github.com/yourusername/ev-advertisement-analysis.git"
    read -r repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        print_info "Pushing to GitHub..."
        git push -u origin main
        print_status "Repository created and pushed to GitHub"
    else
        print_warning "No repository URL provided, skipping GitHub push"
    fi
fi

# Deployment instructions
echo ""
echo "🚀 Deployment Instructions"
echo "========================="
echo ""
print_info "Your dashboard is ready for deployment!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 🌐 GitHub Repository:"
if git remote get-url origin &> /dev/null; then
    repo_url=$(git remote get-url origin)
    echo "   Your code is available at: $repo_url"
else
    echo "   Create a GitHub repository and push your code"
fi
echo ""
echo "2. ☁️  Streamlit Cloud Deployment:"
echo "   • Go to https://share.streamlit.io/"
echo "   • Sign in with your GitHub account"
echo "   • Click 'New app'"
echo "   • Select your repository"
echo "   • Set main file: ev_dashboard.py"
echo "   • Click 'Deploy!'"
echo ""
echo "3. 📊 Data Setup:"
echo "   • Upload your data file (work.csv or similar)"
echo "   • Or modify the app to use file upload widget"
echo "   • Or connect to external data source"
echo ""
echo "4. 🔧 Configuration:"
echo "   • Check .streamlit/config.toml for theme settings"
echo "   • Review requirements.txt for dependencies"
echo "   • Monitor deployment logs for any issues"
echo ""
print_status "Deployment script completed successfully!"
echo ""
print_info "For detailed deployment instructions, see DEPLOYMENT.md"
print_info "For dashboard usage instructions, see DASHBOARD_README.md"
