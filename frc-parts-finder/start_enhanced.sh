#!/bin/bash

# FRC Parts Finder - Enhanced Backend Startup Script

echo "🚀 Starting FRC Parts Finder Enhanced Backend"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/server_enhanced.py" ]; then
    echo "❌ Please run this script from the frc-parts-finder directory"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade build tooling first (Python 3.13 compatibility)
echo "⬆️  Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create cache directory
echo "📁 Creating cache directory..."
mkdir -p cache

# Test the system
echo "🧪 Testing the system..."
python3 test_real_vendors.py

# Start the enhanced server
echo "🌟 Starting enhanced server..."
echo "   - Real vendor integration (WCP, REV, AndyMark, CTRE)"
echo "   - Shopify/WooCommerce search"
echo "   - JSON-LD validation"
echo "   - Smart caching system"
echo ""
echo "🌐 Server will be available at: http://localhost:5001"
echo "📊 Cache stats: http://localhost:5001/api/cache/stats"
echo "🔍 Health check: http://localhost:5001/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 server_enhanced.py
