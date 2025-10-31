#!/usr/bin/env python3
"""
Phoenix Desktop App - Briefcase Entry Point
Launches the Phoenix server in a desktop window
"""

import threading
import time
import webbrowser
import sys
import os
from pathlib import Path
from tkinter import Tk, Label, Button, Frame, Text, Scrollbar
import tkinter.font as tkFont
from typing import Optional
import socket

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
    BASE_DIR = Path(__file__).resolve().parent
    RESOURCE_DIR = BASE_DIR

PROJECT_DIR = BASE_DIR
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class PhoenixApp:
    def __init__(self, root: Tk):
        self.root = root
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        self.server_port = None
        self.app = None
        
        self.setup_window()
        self.show_splash()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Phoenix - Ethereum Bot Monitoring Dashboard")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def show_splash(self):
        """Show splash screen on startup"""
        splash_frame = Frame(self.root, bg="#1a1a1a")
        splash_frame.pack(fill="both", expand=True)
        
        # Title
        title_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        title_label = Label(
            splash_frame,
            text="Phoenix",
            font=title_font,
            bg="#1a1a1a",
            fg="#ffffff"
        )
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_font = tkFont.Font(family="Helvetica", size=12)
        subtitle_label = Label(
            splash_frame,
            text="Ethereum Bot Monitoring Dashboard",
            font=subtitle_font,
            bg="#1a1a1a",
            fg="#888888"
        )
        subtitle_label.pack(pady=10)
        
        # Status
        self.status_label = Label(
            splash_frame,
            text="Initializing...",
            font=subtitle_font,
            bg="#1a1a1a",
            fg="#4a9eff"
        )
        self.status_label.pack(pady=20)
        
        # Start server
        self.root.after(500, self.start_server)
        
    def find_free_port(self) -> int:
        """Find an available port"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]
    
    def start_server(self):
        """Start the FastAPI server in a background thread"""
        self.status_label.config(text="Starting server...")
        self.root.update()
        
        self.server_port = self.find_free_port()
        
        def run_server():
            import uvicorn
            from app.main import app
            
            # Set environment for local operation
            os.environ["HOST"] = "127.0.0.1"
            os.environ["PORT"] = str(self.server_port)
            
            # Ensure static and template paths work in bundled app
            # app.main already handles this, but we set env vars just in case
            os.environ["PROJECT_DIR"] = str(PROJECT_DIR)
            
            try:
                self.server_running = True
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=self.server_port,
                    log_level="warning"  # Reduce logs in GUI
                )
            except Exception as e:
                print(f"Server error: {e}")
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
                # Try again in 100ms
                self.root.after(100, check)
        
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
        header_frame = Frame(main_frame, bg="#1a1a1a", height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        header_label = Label(
            header_frame,
            text="Phoenix Dashboard",
            font=title_font,
            bg="#1a1a1a",
            fg="#ffffff"
        )
        header_label.pack(side="left", padx=20, pady=15)
        
        # URL info
        url_font = tkFont.Font(family="Helvetica", size=10)
        url_label = Label(
            header_frame,
            text=f"Server running on http://127.0.0.1:{self.server_port}",
            font=url_font,
            bg="#1a1a1a",
            fg="#888888"
        )
        url_label.pack(side="right", padx=20, pady=15)
        
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
        
        # Open browser button
        button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        open_button = Button(
            content_frame,
            text="Open Dashboard in Browser",
            font=button_font,
            bg="#4a9eff",
            fg="#ffffff",
            activebackground="#3a8eef",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=10,
            command=self.open_browser
        )
        open_button.pack(pady=20)
        
        # Status/log area
        log_frame = Frame(content_frame, bg="#1a1a1a")
        log_frame.pack(fill="both", expand=True, pady=20)
        
        log_label = Label(
            log_frame,
            text="Status:",
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
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.config(command=self.log_text.yview)
        
        self.log_text.insert("end", f"✓ Server started successfully on port {self.server_port}\n")
        self.log_text.insert("end", f"✓ Ready to receive connections\n")
        self.log_text.config(state="disabled")
        
        # Auto-open browser after a short delay
        self.root.after(1000, self.open_browser)
    
    def open_browser(self):
        """Open the dashboard in the default browser"""
        url = f"http://127.0.0.1:{self.server_port}"
        webbrowser.open(url)
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"✓ Opened browser at {url}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            self.log_text.config(state="normal")
            self.log_text.insert("end", "Shutting down server...\n")
            self.log_text.config(state="disabled")
            # Server will stop when daemon thread exits
        self.root.destroy()


def main():
    """Main entry point for Briefcase"""
    root = Tk()
    app = PhoenixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

