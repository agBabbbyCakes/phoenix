#!/usr/bin/env python3
"""
Standalone desktop application launcher for Phoenix Dashboard.
Uses pywebview to create a native window instead of opening a browser.
"""
import sys
import os
import threading
import time
import socket
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    except Exception:
        pass

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

def start_server(host, port):
    """Start the FastAPI server in a separate thread."""
    import uvicorn
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="warning"  # Reduce console output
        )
    except Exception as e:
        print(f"Server error: {e}")

def wait_for_server(port, timeout=10):
    """Wait for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("127.0.0.1", port))
                if result == 0:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

if __name__ == "__main__":
    try:
        import webview
    except ImportError:
        print("ERROR: pywebview is not installed!")
        print("Please install it with: pip install pywebview")
        sys.exit(1)
    
    # Set environment defaults
    host = os.environ.get("HOST", "127.0.0.1")
    port = find_free_port(int(os.environ.get("PORT", "8000")))
    os.environ["PORT"] = str(port)
    
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    try:
        print("Phoenix Dashboard - Standalone Desktop App")
    except UnicodeEncodeError:
        print("Phoenix Dashboard - Standalone Desktop App")
    print("=" * 60)
    print(f"Starting server on {url}")
    print("Opening native window...")
    print("=" * 60)
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to be ready
    if not wait_for_server(port):
        print("ERROR: Server failed to start")
        sys.exit(1)
    
    # Create native window
    try:
        window_title = "Phoenix Dashboard"
        window = webview.create_window(
            window_title,
            url,
            width=1400,
            height=900,
            min_size=(800, 600),
            resizable=True,
            fullscreen=False,
        )
        
        # Start webview (this blocks until window is closed)
        webview.start(debug=False)
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        try:
            print(f"\nError: {e}")
        except UnicodeEncodeError:
            print(f"\nError: {e}")
        sys.exit(1)

