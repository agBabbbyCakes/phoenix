# Startup Guide - BotScope Dashboard

## 🚀 Quick Start (Recommended)

### Option 1: Using `start.py` (Easiest - Auto Setup)

```bash
python start.py
```

**What this does:**
- ✅ Checks Python 3.11+ is installed
- ✅ Loads `.env` file if present
- ✅ Auto-finds an available port (starts at 8000, tries higher if busy)
- ✅ **If `uv` is installed**: Uses `uv run` (fastest, modern)
- ✅ **If `uv` is NOT installed**: Creates `.venv`, installs dependencies, runs with uvicorn
- ✅ Auto-reload enabled (code changes refresh automatically)
- 🌐 Starts server at `http://localhost:8000` (or next available port)

**This is the best option for new users** - it handles everything automatically!

### Option 2: Using `uv` (Fast, Modern)

```bash
uv run uvicorn app.main:app --reload --port 8000
```

**Prerequisites:** Install `uv` first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**What this does:**
- Uses `uv` for fast dependency management
- Auto-reload on code changes
- Runs on port 8000

### Option 3: Using `app.py` (Simple, No Reload)

```bash
python app.py
```

**What this does:**
- Simple standalone launcher
- No auto-reload (production mode)
- Uses port 8000 (or PORT env var)
- Runs on `127.0.0.1:8000`

### Option 4: Using `scripts/run.sh` (Bash Script)

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

**What this does:**
- Creates `.venv` if needed
- Installs from `requirements.txt`
- Loads `.env` if present
- Auto-reload enabled

### Option 5: Using Makefile

```bash
make run-api
```

**What this does:**
- Uses `uv run` with reload
- Runs on `0.0.0.0:8000` (accessible from network)

## 📋 Setup Checklist

### Before First Run

1. **Check Python Version**
   ```bash
   python3 --version  # Should be 3.11+
   ```

2. **Optional: Install `uv` (Recommended)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Or on macOS:
   ```bash
   brew install uv
   ```

3. **Optional: Create `.env` file** (For Ethereum features)
   ```bash
   # Copy .env.example to .env (if exists)
   # Add your ETH_WSS_URL and CHAINLINK_ETHUSD if needed
   ```

4. **That's it!** Just run `python start.py`

## 🎯 What Happens When You Run `python start.py`

### Step-by-Step Process:

1. **Python Version Check** → Exits if < 3.11
2. **Load Environment** → Reads `.env` file (if exists)
3. **Port Selection** → Finds free port starting from 8000
4. **Dependency Check** → Looks for `uv` command
   - **If found**: Uses `uv run uvicorn app.main:app --reload --port <port>`
   - **If not found**: 
     - Creates `.venv/` virtual environment
     - Upgrades pip
     - Installs: fastapi, uvicorn, jinja2, sse-starlette, python-multipart
     - Runs: `python -m uvicorn app.main:app --reload --port <port>`

5. **Server Starts** → You'll see:
   ```
   [start] Selected free port: 8000
   [start] Using uv: uv run uvicorn app.main:app --reload --port 8000
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Started reloader process
   ```

6. **Open Browser** → Navigate to `http://localhost:8000`

## 🌐 Accessing the Dashboard

Once running, open these URLs:

- **Main Dashboard**: `http://localhost:8000/`
- **Logs Viewer**: `http://localhost:8000/logs`
- **Daily Report**: `http://localhost:8000/report`
- **Demo Page**: `http://localhost:8000/demo`
- **Health Check**: `http://localhost:8000/health`

## 🔧 Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Server Configuration
PORT=8000
HOST=127.0.0.1

# Force Sample Mode (Demo Data)
FORCE_SAMPLE=1

# Real Bot Monitoring (if using Silverback)
SILVERBACK_LOG_PATH=/path/to/recorder.jsonl

# Ethereum Realtime (if using eth_feed)
ETH_WSS_URL=wss://eth-mainnet.alchemyapi.io/v2/YOUR_KEY
CHAINLINK_ETHUSD=0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
```

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## 🔍 Troubleshooting

### Port Already in Use
- `start.py` automatically finds the next available port
- Check what port it selected in the output
- Or set `PORT=8001` in `.env` or environment

### Dependencies Not Installing
```bash
# Manual install with pip
pip install -r requirements.txt
```

### Python Version Too Old
```bash
# Install Python 3.11+
# macOS: brew install python@3.11
# Linux: Use your package manager
```

### Module Not Found Errors
```bash
# Make sure you're in the project root
cd /path/to/phoenix

# Run from project root
python start.py
```

## 📊 Sample Mode vs Real Mode

**Sample Mode (Default):**
- Generates mock trading bot metrics
- No external dependencies needed
- Perfect for demos and testing
- Set `FORCE_SAMPLE=1` to always use

**Real Mode:**
- Connects to live Ethereum data (if configured)
- Tails Silverback JSONL log files
- Requires `SILVERBACK_LOG_PATH` environment variable

## 🎬 Demo the Logs Viewer

1. Start server: `python start.py`
2. Open: `http://localhost:8000/logs`
3. Click: **"🎬 Load Demo"** button
4. Explore: Filters, export, saved queries

## 💡 Pro Tips

1. **Use `start.py`** - It's the most user-friendly option
2. **Install `uv`** - Faster dependency resolution
3. **Enable Auto-reload** - See changes immediately (already enabled)
4. **Bookmark** `/logs` - Quick access to logs viewer
5. **Use `.env`** - Keep configuration separate from code

---

**TL;DR:** Just run `python start.py` and open `http://localhost:8000`! 🚀
