#!/usr/bin/env python3
"""
Enhanced standalone desktop application for Phoenix Dashboard.
Native features: menus, toolbars, system tray, keyboard shortcuts.
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

# Global variables
SERVER_PORT = None
WINDOW_INSTANCE = None

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
            log_level="warning"
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

def get_base_url():
    """Get the base URL for navigation."""
    return f"http://127.0.0.1:{SERVER_PORT}"

def navigate_to(path):
    """Navigate to a specific path in the dashboard."""
    if WINDOW_INSTANCE:
        url = f"{get_base_url()}{path}"
        WINDOW_INSTANCE.load_url(url)

def reload_page():
    """Reload the current page."""
    if WINDOW_INSTANCE:
        WINDOW_INSTANCE.evaluate_js("window.location.reload()")

def go_back():
    """Navigate back in history."""
    if WINDOW_INSTANCE:
        WINDOW_INSTANCE.evaluate_js("window.history.back()")

def go_forward():
    """Navigate forward in history."""
    if WINDOW_INSTANCE:
        WINDOW_INSTANCE.evaluate_js("window.history.forward()")

def show_dev_tools():
    """Show developer tools."""
    if WINDOW_INSTANCE:
        try:
            WINDOW_INSTANCE.show_dev_tools()
        except Exception:
            pass

def create_menu():
    """Create native menu bar for the application."""
    return [
        {
            'label': 'File',
            'submenu': [
                {
                    'label': 'Refresh',
                    'action': reload_page,
                    'shortcut': 'F5'
                },
                {'type': 'separator'},
                {
                    'label': 'Exit',
                    'action': lambda: webview.destroy_window()
                }
            ]
        },
        {
            'label': 'View',
            'submenu': [
                {
                    'label': 'Reload',
                    'action': reload_page,
                    'shortcut': 'Ctrl+R'
                },
                {
                    'label': 'Go Back',
                    'action': go_back,
                    'shortcut': 'Alt+Left'
                },
                {
                    'label': 'Go Forward',
                    'action': go_forward,
                    'shortcut': 'Alt+Right'
                },
                {'type': 'separator'},
                {
                    'label': 'Developer Tools',
                    'action': show_dev_tools,
                    'shortcut': 'F12'
                }
            ]
        },
        {
            'label': 'Dashboard',
            'submenu': [
                {
                    'label': 'Home',
                    'action': lambda: navigate_to('/')
                },
                {
                    'label': 'Bot Explorer',
                    'action': lambda: navigate_to('/explorer')
                },
                {
                    'label': 'Chart Annotations',
                    'action': lambda: navigate_to('/chart-annotations')
                },
                {
                    'label': 'Logic Builder',
                    'action': lambda: navigate_to('/logic-builder')
                },
                {
                    'label': 'Downloads',
                    'action': lambda: navigate_to('/downloads')
                },
                {'type': 'separator'},
                {
                    'label': 'Settings',
                    'action': lambda: navigate_to('/settings')
                }
            ]
        },
        {
            'label': 'Help',
            'submenu': [
                {
                    'label': 'About Phoenix Dashboard',
                    'action': lambda: WINDOW_INSTANCE.evaluate_js(
                        "alert('Phoenix Dashboard\\nNative Desktop Application\\nVersion 0.1.0')"
                    ) if WINDOW_INSTANCE else None
                }
            ]
        }
    ]

if __name__ == "__main__":
    try:
        import webview
    except ImportError:
        print("ERROR: pywebview is not installed!")
        print("Please install it with: pip install pywebview")
        if sys.platform == "linux":
            print("\nFor Linux, you may also need:")
            print("  Ubuntu/Debian: sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev")
            print("  Fedora: sudo dnf install webkit2gtk4.0-devel")
            print("  Arch: sudo pacman -S webkit2gtk")
        sys.exit(1)
    
    # Check for WebKitGTK on Linux
    if sys.platform == "linux":
        try:
            import gi
            gi.require_version('WebKit2', '4.0')
            from gi.repository import WebKit2
        except (ImportError, ValueError) as e:
            print("WARNING: WebKitGTK may not be properly installed")
            print("The app may fall back to opening a browser")
            print("Install: sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev")
            # Continue anyway - pywebview will handle fallback
    
    # Set environment defaults
    host = os.environ.get("HOST", "127.0.0.1")
    SERVER_PORT = find_free_port(int(os.environ.get("PORT", "8000")))
    os.environ["PORT"] = str(SERVER_PORT)
    
    url = f"http://{host}:{SERVER_PORT}"
    
    print("=" * 60)
    try:
        print("Phoenix Dashboard - Native Desktop Application")
    except UnicodeEncodeError:
        print("Phoenix Dashboard - Native Desktop Application")
    print("=" * 60)
    print(f"Starting server on {url}")
    print("Opening native window with desktop features...")
    print("=" * 60)
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=start_server,
        args=(host, SERVER_PORT),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to be ready
    if not wait_for_server(SERVER_PORT):
        print("ERROR: Server failed to start")
        sys.exit(1)
    
    # Create native window with enhanced features
    try:
        window_title = "Phoenix Dashboard"
        
        # Create window with native features
        WINDOW_INSTANCE = webview.create_window(
            window_title,
            url,
            width=1400,
            height=900,
            min_size=(800, 600),
            resizable=True,
            fullscreen=False,
            frameless=False,
            easy_drag=False,
            shadow=True,
            on_top=False,
            text_select=True,
        )
        
        # Start webview with native menu
        try:
            if sys.platform == "darwin":  # macOS has native menu support
                webview.start(debug=False, menu=create_menu())
            else:
                # Windows and Linux - start without menu (can add custom toolbar later)
                webview.start(debug=False)
        except Exception as e:
            # Fallback if menu creation fails
            print(f"Menu creation failed: {e}")
            webview.start(debug=False)
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        try:
            print(f"\nError: {e}")
        except UnicodeEncodeError:
            print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
