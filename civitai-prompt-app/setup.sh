#!/bin/bash
# Quick setup script for Civitai Prompt Generator

echo "🎨 Civitai Prompt Generator - Setup Script"
echo "============================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed!"
    echo "   Install from https://python.org"
    exit 1
fi

echo "✅ Python 3 found"
python3 --version
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the app:"
echo ""
echo "   1. Activate the virtual environment:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Run Streamlit:"
echo "      streamlit run app.py"
echo ""
echo "   3. Open http://localhost:8501 in your browser"
echo ""
echo "💡 Tip: Create an alias in your ~/.bashrc or ~/.zshrc:"
echo "   alias promptgen='cd $(pwd) && source venv/bin/activate && streamlit run app.py'"
echo ""
