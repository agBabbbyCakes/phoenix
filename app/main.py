from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import json, os

from .sse import SSEBroker, client_event_stream
from .data import mock_metrics_publisher, DataStore, tail_jsonl_and_broadcast, parse_bot_log_to_event

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
    # Optional clean UI: redirect to /home when CLEAN_UI is enabled
    if os.getenv("CLEAN_UI", "").lower() in {"1", "true", "yes"}:
        return RedirectResponse(url="/home", status_code=307)
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
    clean_ui = os.getenv("CLEAN_UI", "").lower() in {"1", "true", "yes"}
    if clean_ui:
        # Do not start any publishers; present a clean UI by default
        app.state.sample_mode = False
        return
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


@app.post("/api/logs")
async def receive_bot_logs(request: Request) -> JSONResponse:
    """API endpoint to receive live JSON log data from bots.
    
    Accepts JSONL (newline-delimited JSON) in request body.
    Extracts metrics and updates dashboard in real-time.
    """
    try:
        body = await request.body()
        logs_text = body.decode('utf-8')
        
        # Parse JSONL (newline-delimited JSON) or JSON array
        logs = []
        try:
            # Try as JSON array first
            logs = json.loads(logs_text)
            if not isinstance(logs, list):
                logs = []
        except json.JSONDecodeError:
            # Parse as JSONL (one JSON per line)
            for line in logs_text.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    log_obj = json.loads(line)
                    logs.append(log_obj)
                except json.JSONDecodeError:
                    continue
        
        # Process each log and try to extract metrics
        metrics_created = 0
        for log_obj in logs:
            if not isinstance(log_obj, dict):
                continue
            # Try to parse as a metrics event if it has the right structure
            try:
                event = parse_bot_log_to_event(log_obj)
                if event:
                    store.add(event)
                    metrics_created += 1
            except Exception:
                # If parsing fails, just skip it, don't fail the request
                pass
        
        # Trigger a metrics update broadcast if we created metrics
        if metrics_created > 0:
            kpis = store.kpis()
            labels, values = store.latency_series()
            thr_labels, thr_values = store.throughput_series()
            prof_labels, prof_values = store.profit_series()
            heat = store.heatmap_matrix()
            
            def render_html(name: str, context: dict) -> str:
                template = templates.env.get_template(name)
                return template.render(**context)
            
            html = render_html(
                "partials/metrics.html",
                {
                    "kpis": kpis,
                    "latency_series": list(zip(labels, values)),
                    "throughput_series": list(zip(thr_labels, thr_values)),
                    "profit_series": list(zip(prof_labels, prof_values)),
                    "heatmap": heat,
                    "last_events": store.last_events(25),
                }
            )
            await broker.publish(html)
        
        return JSONResponse({
            "status": "success",
            "logs_received": len(logs),
            "metrics_created": metrics_created
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

