"""Streaming and SSE endpoints."""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_store, get_broker
from app.sse import client_event_stream
from app.data import tail_jsonl_and_broadcast, parse_bot_log_to_event

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


@router.get("/stream")
async def stream(request: Request):
    """SSE stream for real-time metrics updates."""
    broker = get_broker(request)
    return EventSourceResponse(client_event_stream(request, broker))


@router.get("/events")
async def events(request: Request) -> StreamingResponse:
    """Stream events as HTML divs."""
    store = get_store(request)
    
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


@router.get("/silverback/streaming-demo/chart-stream")
async def silverback_streaming_demo_chart_stream(request: Request) -> StreamingResponse:
    """Streams table rows for a Charts.css column chart on the streaming demo page."""
    import random
    
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


@router.get("/logs/stream")
async def logs_stream(request: Request) -> StreamingResponse:
    """Stream logs from Silverback JSONL file or demo data."""
    store = get_store(request)
    
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
                        if line:
                            try:
                                log_obj = json.loads(line.strip())
                                event = parse_bot_log_to_event(log_obj)
                                if event:
                                    store.add(event)
                                    # Render log entry as HTML
                                    html = templates.env.from_string(
                                        """
<div class="log-entry p-2 border-b border-gray-700">
  <div class="flex items-center gap-2 text-xs">
    <span class="opacity-60">{{ timestamp }}</span>
    <span class="font-semibold text-cyan-400">{{ bot_name }}</span>
    <span class="ml-2 font-mono opacity-70">{{ latency }}ms</span>
    {% if error %}<span class="ml-2 text-red-400">{{ error }}</span>{% endif %}
  </div>
</div>
"""
                                    ).render(
                                        timestamp=event.timestamp.strftime("%H:%M:%S"),
                                        bot_name=event.bot_name,
                                        latency=event.latency_ms,
                                        error=event.error,
                                    )
                                    yield html + "\n"
                            except json.JSONDecodeError:
                                pass
                        else:
                            await asyncio.sleep(0.1)
            except Exception as e:
                yield f"<!-- Error reading log file: {e} -->\n"
        else:
            # Demo mode: stream some sample log entries
            import random
            sample_bots = ["arb-scout", "mev-bot", "price-bot", "trade-executor"]
            for _ in range(10):
                try:
                    if await request.is_disconnected():
                        break
                except Exception:
                    break
                bot = random.choice(sample_bots)
                latency = random.randint(50, 500)
                ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                html = templates.env.from_string(
                    """
<div class="log-entry p-2 border-b border-gray-700">
  <div class="flex items-center gap-2 text-xs">
    <span class="opacity-60">{{ timestamp }}</span>
    <span class="font-semibold text-cyan-400">{{ bot_name }}</span>
    <span class="ml-2 font-mono opacity-70">{{ latency }}ms</span>
  </div>
</div>
"""
                ).render(timestamp=ts, bot_name=bot, latency=latency)
                yield html + "\n"
                await asyncio.sleep(1.0)

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@router.post("/silverback/streaming-demo/advisor")
async def silverback_streaming_demo_advisor(request: Request) -> StreamingResponse:
    """Streaming Advisor Bot demo for the Silverback streaming demo page."""
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
            "Monitor bot performance metrics in real-time",
            "Set up automated alerts for critical events",
            "Analyze historical data trends",
            "Optimize bot configurations based on performance"
        ]
        response = f"I can help you with: {', '.join(suggestions[:2])}. Would you like to know more about any of these?"
        now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        yield f'''
<div class="msg bot px-2 py-1 mb-1 border border-gray-700 bg-gray-800/60 rounded">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{now_ts}</span>
    <span class="text-gray-300 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5">{response}</div>
</div>
'''.strip() + "\n"

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@router.get("/advisor")
async def advisor_chat(request: Request) -> StreamingResponse:
    """Advisor chat streaming endpoint."""
    async def stream() -> AsyncIterator[str]:
        yield "<!-- advisor-chat-start -->\n"
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

        response = "I can help you monitor and manage your Ethereum bots. Ask me about performance, metrics, or bot configurations."
        now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        yield f'''
<div class="msg bot px-2 py-1 mb-1 border border-gray-700 bg-gray-800/60 rounded">
  <div class="flex items-center gap-2">
    <span class="opacity-60">{now_ts}</span>
    <span class="text-gray-300 font-semibold">Advisor</span>
  </div>
  <div class="mt-0.5">{response}</div>
</div>
'''.strip() + "\n"

    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")


@router.get("/charts/mini")
async def charts_mini(request: Request) -> StreamingResponse:
    """Mini charts streaming endpoint."""
    store = get_store(request)
    
    async def stream() -> AsyncIterator[str]:
        yield "<!-- charts-mini-start -->\n"
        while True:
            try:
                if await request.is_disconnected():
                    break
            except Exception:
                break
            # Get latest latency value
            events = list(store.events)
            if events:
                latest = events[-1]
                value = latest.latency_ms / 1000.0  # Convert to seconds
                yield f'<li style="--size: {value:.3f};">{value:.3f}s</li>\n'
            await asyncio.sleep(1.0)
    return StreamingResponse(stream(), media_type="text/html; charset=utf-8")

