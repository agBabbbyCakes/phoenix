#!/usr/bin/env python3
"""
Standalone launcher for Phoenix Dashboard.
Opens the web server and automatically opens the browser.
"""
import sys
import os
import webbrowser
import threading
import time
import socket
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def find_free_port(start_port=8000, max_tries=50):
    """Find an available port starting from start_port."""
    for offset in range(max_tries):
        port = start_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    # Fallback: let OS choose
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def open_browser(port, delay=2):
    """Open browser after a short delay."""
    time.sleep(delay)
    url = f"http://127.0.0.1:{port}"
    print(f"\n🌐 Opening browser at {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"   Please open {url} manually in your browser")

if __name__ == "__main__":
    # Set environment defaults
    host = os.environ.get("HOST", "127.0.0.1")
    port = find_free_port(int(os.environ.get("PORT", "8000")))
    os.environ["PORT"] = str(port)
    
    print("=" * 60)
    print("🦍 Phoenix Dashboard - Standalone App")
    print("=" * 60)
    print(f"Starting server on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload in standalone mode
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

