#!/usr/bin/env python3
"""
Launch script for Ethereum Bot Monitoring Dashboard
Usage: python app.py
"""

import sys
import os
from pathlib import Path
import socket

# Add project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    # Set environment defaults if not set
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    ports_env = os.environ.get("PORTS", "").strip()           # e.g. "8000,8001,8002"
    port_range_env = os.environ.get("PORT_RANGE", "").strip()  # e.g. "8000-8100"
    max_tries = 50  # default breadth when no explicit list/range is provided

    def candidate_ports() -> list[int]:
        # Highest precedence: explicit list in PORTS
        if ports_env:
            out = []
            for tok in ports_env.split(","):
                tok = tok.strip()
                if not tok:
                    continue
                try:
                    out.append(int(tok))
                except ValueError:
                    continue
            if out:
                return out
        # Next: range in PORT_RANGE
        if port_range_env and "-" in port_range_env:
            try:
                a, b = port_range_env.split("-", 1)
                start = int(a.strip())
                end = int(b.strip())
                if start <= end:
                    return list(range(start, end + 1))
            except ValueError:
                pass
        # Fallback: try PORT and the next N-1 ports
        return [port + i for i in range(max_tries)]

    def find_open_port(candidates: list[int]) -> int | None:
        for p in candidates:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind((host, p))
                    return p
                except OSError:
                    continue
        return None
    
    ports_to_try = candidate_ports()
    chosen_port = find_open_port(ports_to_try)
    if chosen_port is None:
        print(f"ERROR: No free port found. Tried: {ports_to_try[:10]}{'...' if len(ports_to_try)>10 else ''}")
        sys.exit(1)
    if chosen_port != port:
        print(f"Port {port} unavailable; starting on {chosen_port} (from {len(ports_to_try)} candidates)")
    print(f"Starting Ethereum Bot Monitoring Dashboard on http://{host}:{chosen_port}")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=chosen_port,
            reload=False,  # Disable reload in production/standalone mode
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)

