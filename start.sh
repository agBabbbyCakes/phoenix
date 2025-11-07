#!/bin/bash
# Quick startup script for Silverback Dashboard
# Usage: ./start.sh

echo "🦍 Starting Silverback Dashboard..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Run the Python startup script
python3 start.py

