#!/bin/bash
# Fix OpenSSL issue for Python on macOS

set -e

echo "🔧 Fixing OpenSSL/Python SSL issue..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv not found. Installing pyenv..."
    echo "Run: brew install pyenv"
    exit 1
fi

# Install OpenSSL via Homebrew if not installed
if ! brew list openssl@3 &> /dev/null; then
    echo "📦 Installing OpenSSL 3..."
    brew install openssl@3
fi

# Set OpenSSL paths
export LDFLAGS="-L$(brew --prefix openssl@3)/lib"
export CPPFLAGS="-I$(brew --prefix openssl@3)/include"

# Install Python 3.11.9 (latest stable 3.11)
echo "🐍 Installing Python 3.11.9 with correct OpenSSL..."
pyenv install 3.11.9

# Set as local version
echo "📌 Setting Python 3.11.9 as local version..."
pyenv local 3.11.9

# Verify
echo "✅ Verifying installation..."
python3 --version
python3 -c "import ssl; print('SSL module works!')"

echo ""
echo "✅ Done! You can now run:"
echo "   python3 app.py"
echo "   or"
echo "   python3 start.py"


