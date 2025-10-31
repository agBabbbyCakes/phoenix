#!/usr/bin/env python3
"""
Phoenix Dashboard - Briefcase Entry Point
Launches the Phoenix server and opens browser window
"""

import threading
import sys
import os
import time
from pathlib import Path
from typing import Optional
import socket
import webbrowser
import urllib.request

# Handle resource paths for Briefcase bundling
if getattr(sys, 'frozen', False):
    # Running as a bundled app (Briefcase)
    BASE_DIR = Path(sys.executable).parent
    if (BASE_DIR / "resources").exists():
        RESOURCE_DIR = BASE_DIR / "resources"
    else:
        RESOURCE_DIR = BASE_DIR
else:
    # Running as a script
    BASE_DIR = Path(__file__).resolve().parent.parent
    RESOURCE_DIR = BASE_DIR

PROJECT_DIR = BASE_DIR
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def find_free_port(start_port: int = 8000) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    # Fallback to system-assigned port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_server(server_port: int):
    """Start the FastAPI server in a background thread"""
    try:
        import uvicorn
        from app.main import app
        
        # Set environment for local operation
        os.environ["HOST"] = "127.0.0.1"
        os.environ["PORT"] = str(server_port)
        os.environ["PROJECT_DIR"] = str(PROJECT_DIR)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=server_port,
            log_level="warning"
        )
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            url = f"http://127.0.0.1:{port}/health"
            urllib.request.urlopen(url, timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False


def main():
    """Main entry point for Briefcase"""
    print("=" * 60)
    print("Phoenix Dashboard - Starting...")
    print("=" * 60)
    
    # Find available port
    server_port = find_free_port(8000)
    print(f"✓ Selected port: {server_port}")
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=run_server,
        args=(server_port,),
        daemon=True
    )
    server_thread.start()
    print("✓ Server thread started")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    if wait_for_server(server_port):
        print(f"✓ Server is ready on http://127.0.0.1:{server_port}")
    else:
        print("✗ Server failed to start within timeout")
        sys.exit(1)
    
    # Open browser
    url = f"http://127.0.0.1:{server_port}"
    print(f"🌐 Opening browser at {url}")
    try:
        webbrowser.open(url)
        print("✓ Browser opened")
    except Exception as e:
        print(f"⚠ Could not open browser automatically: {e}")
        print(f"   Please open {url} manually")
    
    print("=" * 60)
    print("Phoenix Dashboard is running!")
    print(f"Dashboard URL: {url}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
            # Check if server thread is still alive
            if not server_thread.is_alive():
                print("\n✗ Server thread died unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
