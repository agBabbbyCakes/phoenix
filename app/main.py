from __future__ import annotations

import asyncio
import json
import os
import random
from collections import deque
import contextlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, Dict, Iterable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(title="Ethereum Bot Monitoring Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


def _generate_tx_hash() -> str:
    full = "0x" + "".join(random.choices("0123456789abcdef", k=64))
    return f"{full[:10]}...{full[-6:]}"


def _generate_bot_name() -> str:
    names = [
        "arb-scout",
        "mev-watch",
        "sandwich-guard",
        "tx-relay",
        "arbit-bot",
        "eth-sniper",
    ]
    return random.choice(names)


class SSEBroker:
    """Simple in-memory pub/sub for SSE clients."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    async def publish(self, message: str) -> None:
        # Best-effort fanout; drop if queue is full
        async with self._lock:
            subscribers = list(self._subscribers)
        for q in subscribers:
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                # Backpressure: drop message for this slow client
                pass


broker = SSEBroker()


async def _client_event_stream(request: Request):
    """Per-client SSE generator that consumes from a dedicated queue."""
    queue = await broker.subscribe()
    try:
        # Initial ping so client can mark connection established
        yield {"event": "ping", "data": "ready"}

        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield {"event": "metrics", "data": message}
            except asyncio.TimeoutError:
                # Periodic keepalive comment (no event/data) could be sent; using ping
                yield {"event": "ping", "data": "keepalive"}
    finally:
        await broker.unsubscribe(queue)


class SuccessWindow:
    """Rolling success rate over a time window."""

    def __init__(self, window_seconds: int = 60) -> None:
        self.window_ms = window_seconds * 1000
        self.events: Deque[tuple[int, bool]] = deque()

    def add(self, now_ms: int, success: bool) -> float:
        self.events.append((now_ms, success))
        cutoff = now_ms - self.window_ms
        while self.events and self.events[0][0] < cutoff:
            self.events.popleft()
        total = len(self.events)
        if total == 0:
            return 0.0
        successes = sum(1 for _, s in self.events if s)
        return round(successes * 100.0 / total, 2)


def _shorten_tx_hash(tx: str) -> str:
    if not isinstance(tx, str) or len(tx) < 12:
        return tx
    if not tx.startswith("0x"):
        tx = "0x" + tx
    return f"{tx[:10]}...{tx[-6:]}"


def _parse_silverback_json(obj: Dict) -> Dict:
    # Timestamp
    ts_iso = None
    if "timestamp" in obj and isinstance(obj["timestamp"], str):
        ts_iso = obj["timestamp"]
    elif "time" in obj and isinstance(obj["time"], str):
        ts_iso = obj["time"]
    elif "ts" in obj and isinstance(obj["ts"], (int, float)):
        ts_iso = datetime.fromtimestamp(obj["ts"], tz=timezone.utc).isoformat()
    else:
        ts_iso = datetime.now(timezone.utc).isoformat()

    # Bot name
    bot = obj.get("bot_name") or obj.get("bot") or obj.get("name") or "silverback"

    # Latency (prefer ms)
    latency_ms: Optional[int] = None
    if isinstance(obj.get("latency_ms"), (int, float)):
        latency_ms = int(obj["latency_ms"])
    elif isinstance(obj.get("latency"), (int, float)):
        # assume seconds -> ms if small number, else treat as ms
        val = float(obj["latency"])
        latency_ms = int(val * 1000 if val < 1000 else val)
    else:
        latency_ms = None

    # Success flag
    success = bool(obj.get("success")) if "success" in obj else bool(obj.get("ok", False))

    # Tx hash
    raw_tx = obj.get("tx_hash") or obj.get("hash") or obj.get("tx") or ""
    tx_hash = _shorten_tx_hash(str(raw_tx)) if raw_tx else _generate_tx_hash()

    # Optional error message
    err = obj.get("error") or obj.get("err") or obj.get("message")

    return {
        "timestamp": ts_iso,
        "bot_name": str(bot),
        "latency_ms": int(latency_ms) if latency_ms is not None else int(random.uniform(40, 450)),
        "success": success,
        "tx_hash": tx_hash,
        "error": str(err) if err is not None else None,
    }


async def _tail_jsonl_and_broadcast(path: Path, from_start: bool = False) -> None:
    """Tail a JSONL file and broadcast parsed metrics to SSE clients.

    If the file is absent, waits and retries. On rotation or truncation, reopens.
    """
    success_window = SuccessWindow(window_seconds=60)
    last_error_logged_at: Optional[float] = None

    while True:
        try:
            if not path.exists():
                await asyncio.sleep(1.0)
                continue

            with path.open("r", encoding="utf-8") as f:
                if not from_start:
                    f.seek(0, 2)  # seek to end

                while True:
                    line = f.readline()
                    if line == "":
                        await asyncio.sleep(0.5)
                        # Detect truncation: if file size < current position, break and reopen
                        try:
                            if f.tell() > path.stat().st_size:
                                break
                        except FileNotFoundError:
                            break
                        continue

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    parsed = _parse_silverback_json(obj)
                    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                    success_rate = success_window.add(now_ms, bool(parsed.get("success", False)))

                    payload = {
                        "timestamp": parsed["timestamp"],
                        "bot_name": parsed["bot_name"],
                        "latency_ms": parsed["latency_ms"],
                        "success_rate": success_rate,
                        "tx_hash": parsed["tx_hash"],
                        "error": parsed.get("error"),
                    }

                    await broker.publish(json.dumps(payload))

        except Exception:
            # Avoid tight error loops; simple backoff
            await asyncio.sleep(1.0)


async def _mock_metrics_publisher() -> None:
    """Fallback mock publisher if no SILVERBACK_JSONL_PATH provided."""
    success_window = SuccessWindow(window_seconds=60)
    while True:
        now = datetime.now(timezone.utc).isoformat()
        latency = int(random.uniform(40, 450))
        success = random.random() > 0.1
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        success_rate = success_window.add(now_ms, success)
        payload = {
            "timestamp": now,
            "bot_name": _generate_bot_name(),
            "latency_ms": latency,
            "success_rate": success_rate,
            "tx_hash": _generate_tx_hash(),
        }
        await broker.publish(json.dumps(payload))
        await asyncio.sleep(2)


@app.get("/stream")
async def stream(request: Request):
    return EventSourceResponse(_client_event_stream(request))


@app.on_event("startup")
async def _on_startup() -> None:
    path_str = os.getenv("SILVERBACK_JSONL_PATH")
    tail_from_start = os.getenv("SILVERBACK_TAIL_FROM_START", "false").lower() in ("1", "true", "yes")
    if path_str:
        app.state.tailer_task = asyncio.create_task(
            _tail_jsonl_and_broadcast(Path(path_str), from_start=tail_from_start)
        )
    else:
        app.state.tailer_task = asyncio.create_task(_mock_metrics_publisher())


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    task: Optional[asyncio.Task] = getattr(app.state, "tailer_task", None)
    if task is not None:
        task.cancel()
        with contextlib.suppress(Exception):
            await task


