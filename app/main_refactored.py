"""Refactored main.py with improved structure."""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.sse import SSEBroker
from app.data import DataStore, mock_metrics_publisher, tail_jsonl_and_broadcast
from app.downloads import router as downloads_router
from app.routers import dashboard
from app.middleware.error_handler import exception_handler_middleware
from app.middleware.rate_limit import RateLimitMiddleware

# Setup logging first
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

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS
cors_origins = ["*"] if settings.cors_allow_all else settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add error handling middleware (as a wrapper)
@app.middleware("http")
async def error_handler_wrapper(request: Request, call_next):
    return await exception_handler_middleware(request, call_next)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(dashboard.router)
app.include_router(downloads_router)

# Mount downloads directory for static file serving (fallback)
DOWNLOADS_DIR = BASE_DIR / "downloads"
if DOWNLOADS_DIR.exists():
    app.mount("/downloads-static", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads-static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize global state
broker = SSEBroker()
store = DataStore(max_events=settings.max_events)

# Store in app state for access in routes
app.state.broker = broker
app.state.store = store


# Health and version endpoints
@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


@app.get("/healthz")
def healthz():
    """Alternative health check endpoint."""
    return {"ok": True}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": BUILD_INFO.get("version_string", settings.app_version)}


@app.on_event("startup")
async def _on_startup() -> None:
    """Startup event handler."""
    def render_html(name: str, context: dict) -> str:
        template = templates.env.get_template(name)
        return template.render(**context)

    # Decide between sample mode (mock) and real tailing
    if settings.clean_ui:
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
    """Shutdown event handler."""
    task: Optional[asyncio.Task] = getattr(app.state, "publisher_task", None)
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

