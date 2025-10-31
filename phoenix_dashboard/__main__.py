#!/usr/bin/env python3
"""
Phoenix Dashboard - Briefcase Entry Point
Launches the Phoenix server and opens an embedded browser window
"""

import threading
import sys
import os
import time
from pathlib import Path
from tkinter import Tk, Label, Button, Frame, Text, Scrollbar, messagebox
import tkinter.font as tkFont
from typing import Optional
import socket
import webbrowser

# Handle resource paths for Briefcase bundling
if getattr(sys, 'frozen', False):
    # Running as a bundled app (Briefcase)
    BASE_DIR = Path(sys.executable).parent
    # Briefcase puts resources in a resources subdirectory
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


class PhoenixDashboard:
    def __init__(self, root: Tk):
        self.root = root
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        self.server_port = 8000
        self.app = None
        
        self.setup_window()
        self.show_splash()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Phoenix Dashboard")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def show_splash(self):
        """Show splash screen on startup"""
        splash_frame = Frame(self.root, bg="#1a1a1a")
        splash_frame.pack(fill="both", expand=True)
        
        # Title
        title_font = tkFont.Font(family="Helvetica", size=28, weight="bold")
        title_label = Label(
            splash_frame,
            text="Phoenix Dashboard",
            font=title_font,
            bg="#1a1a1a",
            fg="#ffffff"
        )
        title_label.pack(pady=60)
        
        # Subtitle
        subtitle_font = tkFont.Font(family="Helvetica", size=12)
        subtitle_label = Label(
            splash_frame,
            text="Silverback recorder and bot controller client",
            font=subtitle_font,
            bg="#1a1a1a",
            fg="#888888"
        )
        subtitle_label.pack(pady=10)
        
        # Version
        version_font = tkFont.Font(family="Helvetica", size=10)
        version_label = Label(
            splash_frame,
            text="Version 0.1.0",
            font=version_font,
            bg="#1a1a1a",
            fg="#555555"
        )
        version_label.pack(pady=5)
        
        # Status
        self.status_label = Label(
            splash_frame,
            text="Initializing...",
            font=subtitle_font,
            bg="#1a1a1a",
            fg="#4a9eff"
        )
        self.status_label.pack(pady=30)
        
        # Start server
        self.root.after(500, self.start_server)
        
    def find_free_port(self, start_port: int = 8000) -> int:
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
    
    def start_server(self):
        """Start the FastAPI server in a background thread"""
        self.status_label.config(text="Starting server...")
        self.root.update()
        
        self.server_port = self.find_free_port(8000)
        
        def run_server():
            try:
                import uvicorn
                from app.main import app
                
                # Set environment for local operation
                os.environ["HOST"] = "127.0.0.1"
                os.environ["PORT"] = str(self.server_port)
                
                # Ensure static and template paths work in bundled app
                os.environ["PROJECT_DIR"] = str(PROJECT_DIR)
                
                self.server_running = True
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=self.server_port,
                    log_level="warning"  # Reduce logs in GUI
                )
            except Exception as e:
                print(f"Server error: {e}")
                self.root.after(0, lambda: self.show_error(str(e)))
            finally:
                self.server_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait for server to be ready
        self.check_server_ready()
    
    def check_server_ready(self):
        """Check if server is ready and then show main window"""
        import urllib.request
        
        def check():
            try:
                url = f"http://127.0.0.1:{self.server_port}/health"
                urllib.request.urlopen(url, timeout=1)
                # Server is ready!
                self.root.after(0, self.show_main_window)
            except:
                # Try again in 200ms
                self.root.after(200, check)
        
        check()
    
    def show_main_window(self):
        """Show the main application window"""
        # Clear splash
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = Frame(self.root, bg="#2a2a2a")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = Frame(main_frame, bg="#1a1a1a", height=70)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        header_label = Label(
            header_frame,
            text="Phoenix Dashboard",
            font=title_font,
            bg="#1a1a1a",
            fg="#ffffff"
        )
        header_label.pack(side="left", padx=20, pady=20)
        
        # URL info
        url_font = tkFont.Font(family="Helvetica", size=10)
        self.url_label = Label(
            header_frame,
            text=f"Server: http://127.0.0.1:{self.server_port}",
            font=url_font,
            bg="#1a1a1a",
            fg="#888888"
        )
        self.url_label.pack(side="right", padx=20, pady=20)
        
        # Content area
        content_frame = Frame(main_frame, bg="#2a2a2a")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        info_font = tkFont.Font(family="Helvetica", size=11)
        info_text = f"""
Phoenix Dashboard is running!

The web interface is available at:
http://127.0.0.1:{self.server_port}

Click the button below to open it in your browser.
        """.strip()
        
        info_label = Label(
            content_frame,
            text=info_text,
            font=info_font,
            bg="#2a2a2a",
            fg="#ffffff",
            justify="left"
        )
        info_label.pack(pady=20)
        
        # Button frame
        button_frame = Frame(content_frame, bg="#2a2a2a")
        button_frame.pack(pady=10)
        
        # Open browser button
        button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        open_button = Button(
            button_frame,
            text="Open Dashboard in Browser",
            font=button_font,
            bg="#4a9eff",
            fg="#ffffff",
            activebackground="#3a8eef",
            activeforeground="#ffffff",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.open_browser
        )
        open_button.pack(side="left", padx=5)
        
        # Refresh button
        refresh_button = Button(
            button_frame,
            text="Refresh",
            font=button_font,
            bg="#666666",
            fg="#ffffff",
            activebackground="#555555",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.refresh_browser
        )
        refresh_button.pack(side="left", padx=5)
        
        # Status/log area
        log_frame = Frame(content_frame, bg="#1a1a1a")
        log_frame.pack(fill="both", expand=True, pady=20)
        
        log_label = Label(
            log_frame,
            text="Status Log:",
            font=info_font,
            bg="#1a1a1a",
            fg="#ffffff",
            anchor="w"
        )
        log_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Scrollable text widget for logs
        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = Text(
            log_frame,
            bg="#1a1a1a",
            fg="#00ff00",
            font=("Courier", 9),
            wrap="word",
            yscrollcommand=scrollbar.set,
            state="disabled"
        )
        self.log_text.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.config(command=self.log_text.yview)
        
        self.log("✓ Server started successfully")
        self.log(f"✓ Listening on port {self.server_port}")
        self.log("✓ Ready to receive connections")
        
        # Auto-open browser after a short delay
        self.root.after(1500, self.open_browser)
    
    def log(self, message: str):
        """Add a message to the log"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def open_browser(self):
        """Open the dashboard in the default browser"""
        url = f"http://127.0.0.1:{self.server_port}"
        try:
            webbrowser.open(url)
            self.log(f"✓ Opened browser at {url}")
        except Exception as e:
            self.log(f"✗ Error opening browser: {e}")
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def refresh_browser(self):
        """Refresh the browser window"""
        self.log("✓ Refreshing browser...")
        # Just log it - user can refresh manually in browser
        self.log("  (Please refresh your browser window manually)")
    
    def show_error(self, error_msg: str):
        """Show an error message"""
        messagebox.showerror("Server Error", f"Failed to start server:\n{error_msg}")
        self.log(f"✗ Error: {error_msg}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            self.log("Shutting down server...")
            # Server will stop when daemon thread exits
        self.root.destroy()


def main():
    """Main entry point for Briefcase"""
    root = Tk()
    app = PhoenixDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()

