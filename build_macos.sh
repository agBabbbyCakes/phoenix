#!/bin/bash
# Build script for macOS installer using Briefcase

set -e

echo "🚀 Building macOS installer for Phoenix Dashboard..."

# Check if briefcase is installed
if ! command -v briefcase &> /dev/null; then
    echo "❌ Briefcase not found. Installing..."
    pip install briefcase
fi

# Clean previous builds (optional)
read -p "Clean previous builds? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning previous builds..."
    rm -rf build/macOS dist/macOS
fi

# Create app structure if it doesn't exist
if [ ! -d "build/macOS" ]; then
    echo "📦 Creating macOS app structure..."
    briefcase create macOS
fi

# Update app code
echo "🔄 Updating app code..."
briefcase update macOS

# Build the app
echo "🔨 Building macOS app..."
briefcase build macOS

# Package as .app bundle
echo "📦 Packaging macOS app..."
briefcase package macOS

echo ""
echo "✅ Build complete!"
echo ""
echo "📱 The macOS app bundle is located at:"
echo "   dist/macOS/Phoenix Dashboard.app"
echo ""
echo "To create a DMG installer, you can use:"
echo "   hdiutil create -volname 'Phoenix Dashboard' -srcfolder 'dist/macOS/Phoenix Dashboard.app' -ov -format UDZO 'dist/macOS/Phoenix Dashboard.dmg'"
echo ""

