from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from .sse import SSEBroker, client_event_stream
from .data import mock_metrics_publisher, DataStore, tail_jsonl_and_broadcast


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(title="Ethereum Bot Monitoring Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


broker = SSEBroker()
store = DataStore()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    sample_mode = getattr(request.app.state, "sample_mode", False)
    return templates.TemplateResponse("index.html", {"request": request, "sample_mode": sample_mode})


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request) -> HTMLResponse:
    summary = store.daily_summary()
    return templates.TemplateResponse("report.html", {"request": request, "summary": summary})


@app.get("/stream")
async def stream(request: Request):
    return EventSourceResponse(client_event_stream(request, broker))


@app.on_event("startup")
async def _on_startup() -> None:
    def render_html(name: str, context: dict) -> str:
        # Use Jinja2 environment to render partial to string
        template = templates.env.get_template(name)
        return template.render(**context)

    # Decide between sample mode (mock) and real tailing
    import os
    log_path = os.getenv("SILVERBACK_LOG_PATH")
    if log_path:
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

