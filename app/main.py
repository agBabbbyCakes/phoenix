from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import json, os

from .sse import SSEBroker, client_event_stream
from .data import mock_metrics_publisher, DataStore, tail_jsonl_and_broadcast

# Optional import for Ethereum realtime feed (only if src directory exists)
try:
    import sys
    from pathlib import Path
    # Add project root to path if src exists
    # This works both locally and in Render/Docker deployments
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.realtime.eth_feed import EthRealtime
    ETH_REALTIME_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    EthRealtime = None
    ETH_REALTIME_AVAILABLE = False

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(title="Ethereum Bot Monitoring Dashboard")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


broker = SSEBroker()
store = DataStore()

# ETH realtime instance (will be created on first use)
eth_rt = None


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Home page with feature overview / start menu."""
    version = os.getenv("APP_VERSION", "0.1.0")
    return templates.TemplateResponse("home.html", {"request": request, "version": version})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    sample_mode = getattr(request.app.state, "sample_mode", False)
    # Build initial metrics HTML so charts render before first SSE update
    kpis = store.kpis()
    labels, values = store.latency_series()
    thr_labels, thr_values = store.throughput_series()
    prof_labels, prof_values = store.profit_series()
    heat = store.heatmap_matrix()
    initial_metrics_html = templates.env.get_template("partials/metrics.html").render(
        {
            "kpis": kpis,
            "latency_series": list(zip(labels, values)),
            "throughput_series": list(zip(thr_labels, thr_values)),
            "profit_series": list(zip(prof_labels, prof_values)),
            "heatmap": heat,
            "last_events": store.last_events(25),
        }
    )
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html},
    )


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request) -> HTMLResponse:
    summary = store.daily_summary()
    return templates.TemplateResponse("report.html", {"request": request, "summary": summary})


@app.get("/demo", response_class=HTMLResponse)
async def demo(request: Request) -> HTMLResponse:
    sample_mode = getattr(request.app.state, "sample_mode", False)
    kpis = store.kpis()
    labels, values = store.latency_series()
    thr_labels, thr_values = store.throughput_series()
    prof_labels, prof_values = store.profit_series()
    heat = store.heatmap_matrix()
    initial_metrics_html = templates.env.get_template("partials/metrics.html").render(
        {
            "kpis": kpis,
            "latency_series": list(zip(labels, values)),
            "throughput_series": list(zip(thr_labels, thr_values)),
            "profit_series": list(zip(prof_labels, prof_values)),
            "heatmap": heat,
            "last_events": store.last_events(25),
        }
    )
    return templates.TemplateResponse(
        "demo.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html},
    )


@app.get("/stream")
async def stream(request: Request):
    # Use the global broker that's already publishing data
    return EventSourceResponse(client_event_stream(request, broker))


@app.on_event("startup")
async def _on_startup() -> None:
    def render_html(name: str, context: dict) -> str:
        # Use Jinja2 environment to render partial to string
        template = templates.env.get_template(name)
        return template.render(**context)

    # Decide between sample mode (mock) and real tailing
    import os
    force_sample = os.getenv("FORCE_SAMPLE", "").lower() in {"1", "true", "yes"}
    log_path = os.getenv("SILVERBACK_LOG_PATH")
    if log_path and not force_sample:
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
    task: Optional[asyncio.Task] = getattr(app.state, "publisher_task", None)
    if task is not None:
        task.cancel()
        with contextlib.suppress(Exception):
            await task


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/version")
def version():
    return {"version": os.getenv("APP_VERSION", "0.1.0")}


@app.get("/logs", response_class=HTMLResponse)
async def logs_viewer(request: Request) -> HTMLResponse:
    """Logs viewer page for displaying JSON log entries."""
    return templates.TemplateResponse("logs.html", {"request": request})

