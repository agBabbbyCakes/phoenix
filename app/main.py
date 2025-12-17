"""Main FastAPI application."""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.sse import SSEBroker
from app.data import mock_metrics_publisher, DataStore, tail_jsonl_and_broadcast
from app.downloads import router as downloads_router
from app.config import settings
from app.logging_config import setup_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import exception_handler_middleware

# Import routers
from app.routers import dashboard, streaming, api, rentals, health

# Setup logging
setup_logging()

# Import version info
try:
    import sys
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from version import get_build_info
    BUILD_INFO = get_build_info()
except Exception:
    BUILD_INFO = {"version": "0.1.0", "build_number": 0, "version_string": "0.1.0"}

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS with settings
# Security: Only allow all origins in development mode (debug=True)
# In production, use specific origins from settings.cors_origins
if settings.debug and settings.cors_allow_all:
    # Development mode - allow all origins
    cors_origins = ["*"]
else:
    # Production mode - use specific origins
    cors_origins = settings.cors_origins if settings.cors_origins else ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if "*" not in cors_origins else False,  # Don't allow credentials with wildcard
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add error handling middleware
@app.middleware("http")
async def error_handler_wrapper(request: Request, call_next):
    return await exception_handler_middleware(request, call_next)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include downloads router for file downloads
app.include_router(downloads_router)

# Mount downloads directory for static file serving (fallback)
DOWNLOADS_DIR = BASE_DIR / "downloads"
if DOWNLOADS_DIR.exists():
    app.mount("/downloads-static", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads-static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize broker and store
broker = SSEBroker()
store = DataStore(max_events=settings.max_events)

# Store in app state for access in routes
app.state.broker = broker
app.state.store = store

# Include all routers
app.include_router(dashboard.router)
app.include_router(streaming.router)
app.include_router(api.router)
app.include_router(rentals.router)
app.include_router(health.router)


@app.on_event("startup")
async def _on_startup() -> None:
    """Startup event handler - initialize data publishers."""
    def render_html(name: str, context: dict) -> str:
        # Use Jinja2 environment to render partial to string
        template = templates.env.get_template(name)
        return template.render(**context)

    # Decide between sample mode (mock) and real tailing
    if settings.clean_ui:
        # Do not start any publishers; present a clean UI by default
        app.state.sample_mode = False
        return
    log_path = settings.silverback_log_path
    if log_path and not settings.force_sample:
        app.state.publisher_task = asyncio.create_task(
            tail_jsonl_and_broadcast(Path(log_path), broker, store, render_html)
        )
        app.state.sample_mode = False
    else:
        app.state.publisher_task = asyncio.create_task(
            mock_metrics_publisher(broker, store, render_html)
        )
        app.state.sample_mode = True


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    """Shutdown event handler - cleanup background tasks."""
    task: Optional[asyncio.Task] = getattr(app.state, "publisher_task", None)
    if task is not None:
        task.cancel()
        # CancelledError inherits from BaseException, not Exception; suppress explicitly.
        with contextlib.suppress(asyncio.CancelledError):
            await task
