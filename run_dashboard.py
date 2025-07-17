#!/usr/bin/env python3
"""
EV Competitor Advert Analysis Dashboard Runner

This script helps you run the Streamlit dashboard for analyzing electric vehicle
advertisements across Portugal, Germany, and Netherlands markets.

Usage:
    python run_dashboard.py

Or directly with streamlit:
    streamlit run streamlit_dashboard.py
"""

import subprocess
import sys
import os


def check_requirements():
    """Check if required packages are installed"""
    required_packages = ["streamlit", "pandas", "plotly", "numpy"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False

    return True


def check_data_file():
    """Check if the data file exists"""
    data_path = "work.csv"

    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        print("\n📁 Please ensure the data file is in the correct location:")
        print(f"   {os.path.abspath(data_path)}")
        return False

    print(f"✅ Data file found: {data_path}")
    return True


def run_dashboard():
    """Run the Streamlit dashboard"""
    print("🚀 Starting EV Competitor Advert Analysis Dashboard...")
    print("📊 Dashboard will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n⏹️  Press Ctrl+C to stop the dashboard")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_dashboard.py",
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")


def main():
    """Main function"""
    print("🚗 EV Competitor Advert Analysis Dashboard")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check data file
    if not check_data_file():
        sys.exit(1)

    print("✅ All checks passed!")
    print()

    # Run dashboard
    run_dashboard()


if __name__ == "__main__":
    main()
