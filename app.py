#!/usr/bin/env python3
"""
Launch script for Ethereum Bot Monitoring Dashboard
Usage: python app.py
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    # Set environment defaults if not set
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    
    print(f"Starting Ethereum Bot Monitoring Dashboard on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload in production/standalone mode
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)

