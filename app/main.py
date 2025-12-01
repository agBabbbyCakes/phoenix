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
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import random
from typing import AsyncIterator

from .sse import SSEBroker, client_event_stream
from .data import mock_metrics_publisher, DataStore, tail_jsonl_and_broadcast, parse_bot_log_to_event
from .models import BotRental, RentalRequest, RentalDuration, PaymentMethod, RentalStatus
from .downloads import router as downloads_router
from .config import settings
from .logging_config import setup_logging
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.error_handler import exception_handler_middleware

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


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS with settings
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


broker = SSEBroker()
store = DataStore(max_events=settings.max_events)

# Store in app state for access in routes
app.state.broker = broker
app.state.store = store

# ETH realtime instance (will be created on first use)
eth_rt = None


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Home page with feature overview / start menu."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("home.html", {"request": request, "version": version})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """IDE Dashboard - Unified interface. Default entry point."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
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
        "ide-dashboard.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html, "version": version},
    )


@app.get("/tv", response_class=HTMLResponse)
async def tv_dashboard(request: Request) -> HTMLResponse:
    """TV-style dashboard (original view)."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
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
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html, "last_events": store.last_events(25), "version": version},
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """New sidebar dashboard layout with Alpine.js."""
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
        "dashboard.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html},
    )


@app.get("/explorer", response_class=HTMLResponse)
async def bot_explorer_page(request: Request) -> HTMLResponse:
    """Bot Explorer page - Etherscan meets stock research."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("bot-explorer.html", {"request": request, "version": version})


@app.get("/logic-builder", response_class=HTMLResponse)
async def logic_builder_page(request: Request) -> HTMLResponse:
    """Visual conditional logic builder page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("logic-builder.html", {"request": request, "version": version})


@app.get("/chart-annotations", response_class=HTMLResponse)
async def chart_annotations_page(request: Request) -> HTMLResponse:
    """Chart annotations and event triggers page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("chart-annotations.html", {"request": request, "version": version})


@app.get("/bots", response_class=HTMLResponse)
async def bots_page(request: Request) -> HTMLResponse:
    """Bots management page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("bots.html", {"request": request, "version": version})


@app.get("/bots/{bot_id}", response_class=HTMLResponse)
async def bot_profile(request: Request, bot_id: str) -> HTMLResponse:
    """Individual bot profile page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("bot-profile.html", {"request": request, "bot_id": bot_id, "version": version})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request) -> HTMLResponse:
    """Settings page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("settings.html", {"request": request, "version": version})


@app.get("/downloads", response_class=HTMLResponse)
async def downloads_page(request: Request) -> HTMLResponse:
    """Downloads page for standalone applications."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("downloads.html", {"request": request, "version": version})


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


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    async def stream():
        last_sent_index = 0
        # Initial small chunk to kick off streaming
        yield "<!-- event-stream-start -->\n"
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            events = list(store.events)
            while last_sent_index < len(events):
                e = events[last_sent_index]
                last_sent_index += 1
                # Determine status styling
                ok = (e.error is None) and (e.status in (None, "ok"))
                status_class = "text-emerald-400"
                if not ok and (e.status == "warning"):
                    status_class = "text-yellow-400"
                elif not ok:
                    status_class = "text-red-400"
                # Render a compact event row (Div component)
                html = templates.env.from_string(
                    """
<div class="event-item flex items-center gap-2 py-1 text-xs">
  <span class="opacity-60">{{ ts }}</span>
  <span class="font-semibold">{{ bot }}</span>
  <span class="ml-2 font-mono opacity-70">{{ latency }}</span>
  <span class="ml-2 {{ status_class }}">{{ status_text }}</span>
  {% if tx %}<span class="ml-2 font-mono text-[10px] opacity-70">{{ tx }}</span>{% endif %}
</div>
"""
                ).render(
                    ts=e.timestamp.strftime("%H:%M:%S"),
                    bot=e.bot_name,
                    latency=f"{int(e.latency_ms)}ms",
                    status_class=status_class,
                    status_text=("OK" if ok else (str(e.status or "error")).upper()),
                    tx=e.tx_hash,
                )
                # Each yield flushes immediately to the client
                yield html + "\n"
            # Idle wait before checking for new events
            await asyncio.sleep(0.5)

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")

@app.get("/silverback/streaming-demo/chart-stream")
async def silverback_streaming_demo_chart_stream(request: Request) -> StreamingResponse:
    """Streams table rows for a Charts.css column chart on the streaming demo page."""
    async def stream() -> AsyncIterator[str]:
        yield "<!-- streaming-demo-chart-rows -->\n"
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            val = random.randint(0, 100)
            row = templates.env.from_string(
                """
<tr>
  <td class="font-mono text-xs opacity-70">{{ ts }}</td>
  <td data-c="{{ val }}">{{ val }}</td>
</tr>
"""
            ).render(ts=ts, val=val)
            yield row + "\n"
            await asyncio.sleep(random.uniform(0.6, 1.6))
    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@app.get("/logs/stream")
async def logs_stream(request: Request) -> StreamingResponse:
    async def stream():
        # Start the stream with a small chunk for immediate flush
        yield "<!-- logs-stream-start -->\n"
        # If a Silverback JSONL log path is configured, tail that file; else stream demo lines
        log_path = os.getenv("SILVERBACK_LOG_PATH")
        if log_path and Path(log_path).exists():
            try:
                with Path(log_path).open("r", encoding="utf-8") as f:
                    # Start tailing from end of file (live only)
                    f.seek(0, 2)
                    while True:
                        try:
                            if await request.is_disconnected():
                                break
                        except Exception:
                            break
                        line = f.readline()
                        if line == "":
                            # No new line; small idle sleep and continue
                            await asyncio.sleep(0.3)
                            # Handle file truncation/rotation
                            try:
                                if f.tell() > Path(log_path).stat().st_size:
                                    break
                            except FileNotFoundError:
                                break
                            continue
                        line = line.strip()
                        if not line:
                            continue
                        # Try JSON parse; fallback to raw message
                        ts_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
                        level_name = "INFO"
                        level_class = "text-blue-400"
                        message = line
                        try:
                            obj = json.loads(line)
                            message = str(obj.get("message", line))
                            # timestamp normalization
                            raw_ts = obj.get("timestamp") or obj.get("time")
                            if isinstance(raw_ts, str):
                                try:
                                    ts_dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                                    ts_str = ts_dt.strftime("%H:%M:%S")
                                except Exception:
                                    ts_str = str(raw_ts)
                            # map level
                            level = obj.get("level")
                            if isinstance(level, int):
                                if level >= 50:
                                    level_name, level_class = "CRITICAL", "text-red-600"
                                elif level >= 40:
                                    level_name, level_class = "ERROR", "text-red-400"
                                elif level >= 30:
                                    level_name, level_class = "WARN", "text-yellow-400"
                                elif level >= 20:
                                    level_name, level_class = "INFO", "text-blue-400"
                                else:
                                    level_name, level_class = f"LVL-{level}", "text-gray-400"
                        except Exception:
                            # keep defaults for raw line
                            pass
                        html = templates.env.from_string(
                            """
<div class="log-line flex items-center gap-2 py-1 text-xs">
  <span class="opacity-60">{{ ts }}</span>
  <span class="{{ level_class }} font-semibold">[{{ level_name }}]</span>
  <span class="whitespace-pre-wrap break-words">{{ message }}</span>
</div>
"""
                        ).render(ts=ts_str, level_name=level_name, level_class=level_class, message=message)
                        yield html + "\n"
            except Exception:
                # If file tailing fails, fall back to demo stream
                pass
        # Demo/sample streaming fallback
        import random
        levels = [
            ("INFO", "text-blue-400"),
            ("WARN", "text-yellow-400"),
            ("ERROR", "text-red-400"),
        ]
        bots = ["arb-scout", "mev-watch", "sandwich-guard", "tx-relay", "eth-sniper"]
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            now = datetime.now(timezone.utc).strftime("%H:%M:%S")
            lvl, cls = random.choice(levels)
            bot = random.choice(bots)
            msg = f"{bot}: simulated {lvl.lower()} event - latency={random.randint(50,450)}ms"
            html = templates.env.from_string(
                """
<div class="log-line flex items-center gap-2 py-1 text-xs">
  <span class="opacity-60">{{ ts }}</span>
  <span class="{{ level_class }} font-semibold">[{{ level_name }}]</span>
  <span class="whitespace-pre-wrap break-words">{{ message }}</span>
</div>
"""
            ).render(ts=now, level_name=lvl, level_class=cls, message=msg)
            yield html + "\n"
            await asyncio.sleep(random.uniform(0.8, 2.2))

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")

@app.post("/silverback/streaming-demo/advisor")
async def silverback_streaming_demo_advisor(request: Request) -> StreamingResponse:
    """Streaming Advisor Bot demo for the Silverback streaming demo page.
    
    Accepts a 'question' field (form or JSON) and streams a sequence of Divs:
      1) Echo of the user's question
      2) 'Thinking...' placeholder
      3) Final advisor-style response
    """
    async def stream() -> AsyncIterator[str]:
        yield "<!-- streaming-demo-advisor-start -->\n"
        # Extract question from form (preferred for HTMX), fall back to JSON
        question = ""
        try:
            form = await request.form()
            question = str(form.get("question") or "").strip()
        except Exception:
            pass
        if not question:
            try:
                data = await request.json()
                question = str(data.get("question") or "").strip()
            except Exception:
                question = ""
        if not question:
            question = "What can you do?"

        now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        # 1) Echo user question
        yield f'''
<div class="msg user px-2 py-1 mb-1 border border-blue-500/30 bg-blue-500/10 rounded">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{now_ts}</span>
    <span class="text-blue-400 font-semibold">You</span>
  </div>
  <div class="mt-0.5">You: {question}</div>
</div>
'''.strip() + "\n"
        await asyncio.sleep(0.5)

        # 2) Thinking placeholder
        now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        yield f'''
<div class="msg bot px-2 py-1 mb-1 border border-gray-700 bg-gray-800/60 rounded">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{now_ts}</span>
    <span class="text-gray-300 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5 italic opacity-80">Thinking&hellip;</div>
</div>
'''.strip() + "\n"
        await asyncio.sleep(1.0)

        # 3) Final advisor response
        suggestions = [
            "Here's what Silverback recommends: review recent latency spikes and adjust alert thresholds.",
            "Here's what Silverback recommends: check tx-relay queue depth; consider backpressure on submissions.",
            "Here's what Silverback recommends: minor rebalancing across bots to smooth throughput.",
            "Here's what Silverback recommends: hold non-critical sends; gas volatility detected.",
            "Here's what Silverback recommends: tighten slippage temporarily to reduce frontrun risk.",
        ]
        answer = random.choice(suggestions)
        now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        yield f'''
<div class="msg bot px-2 py-1 mb-1 border border-emerald-500/30 bg-emerald-500/10 rounded">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{now_ts}</span>
    <span class="text-emerald-400 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5">Advisor: {answer}</div>
</div>
'''.strip() + "\n"

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@app.get("/advisor")
async def advisor_stream(request: Request) -> StreamingResponse:
    async def stream():
        yield "<!-- advisor-stream-start -->\n"
        tips = [
            "Consider raising latency alert threshold by 10% based on last-minute volatility.",
            "arb-scout shows elevated latency; investigate upstream RPC provider.",
            "mev-watch success rate dipped to 82% — check recent bundle rejections.",
            "Opportunity detected: widening spread suggests short-lived arbitrage.",
            "High gas detected; defer non-urgent transactions for 2–3 blocks.",
            "Sandwich-guard flagged potential frontrun pattern; tighten slippage.",
            "tx-relay queue depth rising — enable backpressure on submissions.",
            "Bot allocation skewed; rebalance CPU time toward strategy-bot.",
        ]
        badges = [
            ("info", "text-blue-400", "bg-blue-500/10 border-blue-500/30"),
            ("warn", "text-yellow-400", "bg-yellow-500/10 border-yellow-500/30"),
            ("crit", "text-red-400", "bg-red-500/10 border-red-500/30"),
            ("ok", "text-emerald-400", "bg-emerald-500/10 border-emerald-500/30"),
        ]
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            level, color, frame = random.choice(badges)
            msg = random.choice(tips)
            html = templates.env.from_string(
                """
<div class="advisor-line text-xs border rounded px-2 py-1 mb-1 {{ frame }}">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{{ ts }}</span>
    <span class="{{ color }} font-semibold uppercase">Advisor</span>
  </div>
  <div class="mt-0.5">{{ msg }}</div>
</div>
"""
            ).render(ts=ts, color=color, frame=frame, msg=msg)
            yield html + "\n"
            await asyncio.sleep(random.uniform(1.5, 3.5))

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@app.get("/charts/mini")
async def charts_mini_stream(request: Request) -> StreamingResponse:
    async def stream():
        yield "<!-- mini-chart-stream-start -->\n"
        # Stream small bar entries as Charts.css <li> items, one per tick
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            # Normalize to 0..1 for --size
            val = random.uniform(0.05, 0.95)
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            html = templates.env.from_string(
                """
<li style="--size: {{ size }};">
  <span class="data">{{ label }}</span>
</li>
"""
            ).render(size=f"{val:.3f}", label=ts)
            yield html + "\n"
            await asyncio.sleep(random.uniform(1.0, 2.0))

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")

@app.post("/advisor")
async def advisor_chat(request: Request) -> StreamingResponse:
    async def stream():
        yield "<!-- advisor-chat-start -->\n"
        # Extract question from form or JSON
        question = ""
        try:
            # Prefer form data (HTMX default)
            form = await request.form()
            question = str(form.get("q") or "").strip()
        except Exception:
            question = ""
        if not question:
            try:
                data = await request.json()
                question = str(data.get("q") or "").strip()
            except Exception:
                question = ""
        if not question:
            question = "What can you do?"

        # 1) Echo the question
        echo_html = templates.env.from_string(
            """
<div class="advisor-line text-xs border rounded px-2 py-1 mb-1 bg-blue-500/10 border-blue-500/30">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{{ ts }}</span>
    <span class="text-blue-400 font-semibold">You</span>
  </div>
  <div class="mt-0.5">{{ question }}</div>
</div>
"""
        ).render(ts=datetime.now(timezone.utc).strftime("%H:%M:%S"), question=question)
        yield echo_html + "\n"
        await asyncio.sleep(0.4)

        # 2) Thinking...
        thinking_html = templates.env.from_string(
            """
<div class="advisor-line text-xs border rounded px-2 py-1 mb-1 bg-gray-800/60 border-gray-700">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{{ ts }}</span>
    <span class="text-gray-300 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5 italic opacity-80">Thinking&hellip;</div>
</div>
"""
        ).render(ts=datetime.now(timezone.utc).strftime("%H:%M:%S"))
        yield thinking_html + "\n"
        await asyncio.sleep(1.0)

        # 3) Final advisor message (simple heuristic response)
        tip_bank = [
            "Consider examining recent latency spikes and adjusting your alert thresholds.",
            "Review recent error logs for tx-relay; queue depth may be increasing.",
            "Throughput looks uneven across bots — a small rebalance could help.",
            "Gas conditions are volatile; consider postponing non-critical sends.",
            "Enable more conservative slippage for sandwich-guard temporarily.",
        ]
        import random as _rnd
        picked = _rnd.choice(tip_bank)
        final_html = templates.env.from_string(
            """
<div class="advisor-line text-xs border rounded px-2 py-1 mb-1 bg-emerald-500/10 border-emerald-500/30">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{{ ts }}</span>
    <span class="text-emerald-400 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5">{{ answer }}</div>
</div>
"""
        ).render(ts=datetime.now(timezone.utc).strftime("%H:%M:%S"), answer=f"{picked} (Q: {question})")
        yield final_html + "\n"

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")

@app.on_event("startup")
async def _on_startup() -> None:
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
    task: Optional[asyncio.Task] = getattr(app.state, "publisher_task", None)
    if task is not None:
        task.cancel()
        # CancelledError inherits from BaseException, not Exception; suppress explicitly.
        with contextlib.suppress(asyncio.CancelledError):
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


@app.get("/pointcloud", response_class=HTMLResponse)
async def pointcloud_viewer(request: Request) -> HTMLResponse:
    """Standalone 3D point cloud visualization page."""
    version = BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))
    return templates.TemplateResponse("pointcloud.html", {"request": request, "version": version})


@app.get("/api/bots/status")
async def get_bots_status() -> JSONResponse:
    """Get aggregated health status for all bots.
    
    Returns bot name, last heartbeat, success ratio, failure count, 
    last block, and latency for each bot.
    """
    from datetime import datetime, timezone
    
    # Aggregate events by bot name
    bot_stats = {}
    events = list(store.events)
    
    for event in events:
        bot_name = event.bot_name
        if bot_name not in bot_stats:
            bot_stats[bot_name] = {
                "bot_name": bot_name,
                "last_heartbeat": None,
                "success_count": 0,
                "failure_count": 0,
                "total_count": 0,
                "latencies": [],
                "last_block": None,  # Not available in current model
            }
        
        stats = bot_stats[bot_name]
        
        # Update last heartbeat (most recent timestamp)
        if stats["last_heartbeat"] is None or event.timestamp > stats["last_heartbeat"]:
            stats["last_heartbeat"] = event.timestamp
        
        # Count successes and failures
        stats["total_count"] += 1
        if event.error is None and event.status in (None, "ok"):
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1
        
        # Collect latencies
        if event.latency_ms:
            stats["latencies"].append(event.latency_ms)
    
    # Convert to response format
    bots = []
    for bot_name, stats in bot_stats.items():
        # Calculate success ratio
        success_ratio = 0.0
        if stats["total_count"] > 0:
            success_ratio = (stats["success_count"] / stats["total_count"]) * 100.0
        
        # Calculate average latency
        avg_latency = 0
        if stats["latencies"]:
            avg_latency = int(sum(stats["latencies"]) / len(stats["latencies"]))
        
        # Format last heartbeat as ISO string
        last_heartbeat = None
        if stats["last_heartbeat"]:
            last_heartbeat = stats["last_heartbeat"].isoformat()
        
        bots.append({
            "bot_name": bot_name,
            "name": bot_name,  # Alias for compatibility
            "last_heartbeat": last_heartbeat,
            "success_ratio": round(success_ratio, 2),
            "failure_count": stats["failure_count"],
            "last_block": stats["last_block"],
            "latency_ms": avg_latency,
            "latency": avg_latency,  # Alias for compatibility
        })
    
    return JSONResponse({"bots": bots})


@app.get("/api/charts/data")
async def get_charts_data() -> JSONResponse:
    """Get chart data in JSON format for 3D visualizations.
    
    Returns recent events with all metrics for chart rendering.
    """
    events = store.last_events(100)  # Get last 100 events
    
    chart_data = []
    for event in events:
        chart_data.append({
            "timestamp": event.timestamp.isoformat(),
            "bot_name": event.bot_name,
            "latency_ms": event.latency_ms,
            "latency": event.latency_ms,
            "success_rate": event.success_rate if hasattr(event, 'success_rate') else None,
            "success_ratio": event.success_rate if hasattr(event, 'success_rate') else None,
            "profit": event.profit if hasattr(event, 'profit') else None,
            "status": event.status,
            "error": event.error,
            "tx_hash": event.tx_hash if hasattr(event, 'tx_hash') else None,
        })
    
    return JSONResponse({
        "events": chart_data,
        "count": len(chart_data),
        "kpis": store.kpis()
    })


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


# Bot Rental Endpoints
@app.post("/api/bots/rent")
async def rent_bot(request: RentalRequest) -> JSONResponse:
    """Rent a bot for a specified duration.
    
    Creates a rental record and returns rental information.
    In production, this would integrate with payment processing.
    """
    try:
        from datetime import timedelta
        
        # Calculate expiration time based on duration
        now = datetime.now(timezone.utc)
        if request.duration == RentalDuration.HOURLY:
            expires_at = now + timedelta(hours=1)
            base_price = 0.5  # Base hourly price
        elif request.duration == RentalDuration.DAILY:
            expires_at = now + timedelta(days=1)
            base_price = 12.0  # Daily price
        elif request.duration == RentalDuration.MONTHLY:
            expires_at = now + timedelta(days=30)
            base_price = 300.0  # Monthly price (with discount)
        else:
            return JSONResponse({"status": "error", "message": "Invalid duration"}, status_code=400)
        
        # Get bot info to calculate price
        bot_stats = {}
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == request.bot_id:
                bot_stats["bot_name"] = event.bot_name
                break
        
        # Create rental record
        rental = BotRental(
            bot_id=request.bot_id,
            bot_name=bot_stats.get("bot_name", request.bot_id),
            duration=request.duration,
            price=base_price,
            payment_method=request.payment_method,
            status=RentalStatus.ACTIVE,
            rented_at=now,
            expires_at=expires_at
        )
        
        # In production, store in database
        # For now, return success response
        return JSONResponse({
            "status": "success",
            "rental": {
                "id": f"rental_{request.bot_id}_{int(now.timestamp())}",
                "bot_id": rental.bot_id,
                "bot_name": rental.bot_name,
                "duration": rental.duration.value,
                "price": rental.price,
                "status": rental.status.value,
                "rented_at": rental.rented_at.isoformat(),
                "expires_at": rental.expires_at.isoformat()
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/api/bots/rentals")
async def get_rentals() -> JSONResponse:
    """Get all active rentals for the current user.
    
    Returns list of active bot rentals.
    """
    # In production, filter by user_id
    # For now, return empty list (rentals stored client-side)
    return JSONResponse({
        "status": "success",
        "rentals": []
    })


@app.get("/api/bots/{bot_id}/rental-info")
async def get_bot_rental_info(bot_id: str) -> JSONResponse:
    """Get rental information and pricing for a specific bot.
    
    Returns pricing tiers and availability.
    """
    try:
        # Get bot stats
        bot_stats = {}
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == bot_id:
                bot_stats["bot_name"] = event.bot_name
                break
        
        # Calculate pricing based on bot type/strategy
        strategy = "arbitrage"  # Default
        if "mev" in bot_id.lower():
            strategy = "mev"
        elif "trade" in bot_id.lower() or "snipe" in bot_id.lower():
            strategy = "trading"
        elif "monitor" in bot_id.lower():
            strategy = "monitoring"
        
        base_prices = {
            "arbitrage": 0.5,
            "mev": 0.8,
            "trading": 0.6,
            "monitoring": 0.3,
            "defi": 0.7,
            "nft": 0.4
        }
        
        hourly_price = base_prices.get(strategy, 0.5)
        daily_price = hourly_price * 24
        monthly_price = hourly_price * 24 * 30 * 0.8  # 20% discount
        
        return JSONResponse({
            "status": "success",
            "bot_id": bot_id,
            "bot_name": bot_stats.get("bot_name", bot_id),
            "pricing": {
                "hourly": round(hourly_price, 2),
                "daily": round(daily_price, 2),
                "monthly": round(monthly_price, 2)
            },
            "available": True
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.delete("/api/bots/rentals/{rental_id}")
async def cancel_rental(rental_id: str) -> JSONResponse:
    """Cancel an active rental.
    
    Marks rental as cancelled and processes refund if applicable.
    """
    try:
        # In production, update rental status in database
        return JSONResponse({
            "status": "success",
            "message": f"Rental {rental_id} cancelled successfully"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.post("/api/bots/trade")
async def trade_bot(request: Request) -> JSONResponse:
    """Trade bot shares (buy/sell).
    
    Allows users to buy or sell shares of high-performing bots.
    In production, this would integrate with a trading system.
    """
    try:
        data = await request.json()
        bot_id = data.get("bot_id")
        trade_type = data.get("type")  # 'buy' or 'sell'
        amount = float(data.get("amount", 0))
        price = float(data.get("price", 0))
        
        if not bot_id or amount <= 0 or price <= 0:
            return JSONResponse({"status": "error", "message": "Invalid trade parameters"}, status_code=400)
        
        total_cost = amount * price
        
        # In production, this would:
        # 1. Validate user balance
        # 2. Execute trade on exchange/marketplace
        # 3. Update user portfolio
        # 4. Record transaction
        
        return JSONResponse({
            "status": "success",
            "trade": {
                "bot_id": bot_id,
                "type": trade_type,
                "amount": amount,
                "price": price,
                "total": total_cost,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/api/live/{metric}")
async def get_live_metric(metric: str) -> JSONResponse:
    """Get live metric data for charts.
    
    Supported metrics: latency, throughput, profit, success_rate
    Returns: { timestamps: [...], values: [...] }
    """
    # Get recent events
    events = store.last_events(60)  # Last 60 events
    
    if not events:
        # Return empty data if no events
        return JSONResponse({
            "timestamps": [],
            "values": []
        })
    
    # Extract data based on metric
    timestamps = []
    values = []
    
    for event in events:
        # Convert timestamp to milliseconds since epoch
        ts_ms = int(event.timestamp.timestamp() * 1000)
        timestamps.append(ts_ms)
        
        if metric == "latency":
            values.append(event.latency_ms)
        elif metric == "throughput":
            # Count events per time window (simplified - just use 1 per event)
            values.append(1)
        elif metric == "profit":
            values.append(event.profit if event.profit is not None else 0.0)
        elif metric == "success_rate":
            # Calculate success rate (1 if no error, 0 if error)
            values.append(100.0 if event.error is None else 0.0)
        else:
            # Default to latency
            values.append(event.latency_ms)
    
    return JSONResponse({
        "timestamps": timestamps,
        "values": values
    })


@app.get("/api/bots/{bot_id}/trading-info")
async def get_bot_trading_info(bot_id: str) -> JSONResponse:
    """Get trading information for a bot (price, volume, market data).
    
    Returns current market price, 24h volume, and trading statistics.
    """
    try:
        # Get bot stats
        bot_stats = {}
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == bot_id:
                bot_stats["bot_name"] = event.bot_name
                bot_stats["success_rate"] = event.success_rate
                break
        
        # Calculate market price based on performance
        base_price = 0.5
        if bot_stats.get("success_rate", 0) > 95:
            base_price = 1.0
        elif bot_stats.get("success_rate", 0) > 90:
            base_price = 0.75
        elif bot_stats.get("success_rate", 0) > 80:
            base_price = 0.5
        
        share_price = base_price * 100  # Convert to share price
        
        return JSONResponse({
            "status": "success",
            "bot_id": bot_id,
            "bot_name": bot_stats.get("bot_name", bot_id),
            "market_data": {
                "current_price": share_price,
                "24h_volume": random.randint(10000, 1000000),
                "24h_high": share_price * 1.1,
                "24h_low": share_price * 0.9,
                "market_cap": share_price * 1000000,  # Simulated
                "available_shares": 1000000
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

