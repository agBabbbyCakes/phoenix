# Quick Fix for OpenSSL/SSL Error on macOS

## The Problem
```
ImportError: dlopen(.../_ssl.cpython-39-darwin.so, 0x0002): 
Library not loaded: /opt/homebrew/opt/openssl@1.1/lib/libssl.1.1.dylib
```

Your Python 3.9.9 was compiled against OpenSSL 1.1 which is no longer available.

## Quick Fix (Choose One)

### Option 1: Reinstall Python with Correct OpenSSL (Recommended)

```bash
# Install OpenSSL 3
brew install openssl@3

# Set environment variables
export LDFLAGS="-L$(brew --prefix openssl@3)/lib"
export CPPFLAGS="-I$(brew --prefix openssl@3)/include"

# Install Python 3.11.9
pyenv install 3.11.9

# Use it for this project
pyenv local 3.11.9

# Verify it works
python3 -c "import ssl; print('SSL works!')"

# Now run the app
python3 app.py
```

### Option 2: Use System Python (If Available)

```bash
# Check if system Python works
/usr/bin/python3 --version
/usr/bin/python3 -c "import ssl; print('OK')"

# If it works, use it
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Option 3: Use the Fix Script

```bash
chmod +x fix_openssl.sh
./fix_openssl.sh
```

### Option 4: Use Docker (If Available)

```bash
docker build -t phoenix .
docker run -p 8000:8000 phoenix
```

## After Fixing

Once SSL is working, you can run:

```bash
# Method 1: Direct
python3 app.py

# Method 2: With start.py (requires Python 3.11+)
python3 start.py

# Method 3: With Makefile (if uv is installed)
make run-api

# Method 4: With uvicorn directly
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verify It's Fixed

```bash
python3 -c "import ssl; import uvicorn; print('✅ All good!')"
```

If you see "✅ All good!", you're ready to run the app!


