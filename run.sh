#!/usr/bin/env bash
# SmartInsight AI Startup Script

echo "🚀 Starting SmartInsight AI..."
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed."
    exit 1
fi

# Install requirements
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run the app
echo "🎬 Launching SmartInsight AI..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Open your browser to: http://localhost:8501"
echo "ℹ️  First run will take 2-3 minutes to train models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run Home.py
