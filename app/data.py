from __future__ import annotations

import asyncio
import json
import random
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque

from .models import MetricsEvent
from .sse import SSEBroker


class SuccessWindow:
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


def _random_tx_hash() -> str:
    s = "0x" + "".join(random.choice("0123456789abcdef") for _ in range(64))
    return f"{s[:10]}...{s[-6:]}"


def _random_bot() -> str:
    return random.choice([
        "arb-scout",
        "mev-watch",
        "sandwich-guard",
        "tx-relay",
        "arbit-bot",
        "eth-sniper",
    ])


class DataStore:
    """In-memory store of recent events and kpi aggregations."""

    def __init__(self, max_events: int = 1000) -> None:
        self.events: Deque[MetricsEvent] = deque(maxlen=max_events)

    def add(self, evt: MetricsEvent) -> None:
        self.events.append(evt)

    def last_events(self, n: int = 25) -> list[MetricsEvent]:
        return list(self.events)[-n:][::-1]

    def kpis(self) -> dict:
        items = list(self.events)
        if not items:
            return {"avg_latency_ms": 0, "success_rate_pct": 0.0, "throughput_1m": 0, "avg_profit": 0.0}
        # Avg latency
        avg_latency = sum(e.latency_ms for e in items) / len(items)
        # Success rate as last 60s successes / total
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        cutoff = now_ms - 60_000
        last_minute = [e for e in items if int(e.timestamp.timestamp() * 1000) >= cutoff]
        if last_minute:
            successes = sum(1 for _e in last_minute if (_e.error is None))
            success_rate = round(successes * 100.0 / len(last_minute), 2)
        else:
            success_rate = 0.0
        throughput = len(last_minute)
        avg_profit = 0.0
        profits = [e.profit for e in items if isinstance(e.profit, (int, float))]
        if profits:
            avg_profit = round(sum(profits) / len(profits), 2)
        return {
            "avg_latency_ms": int(avg_latency),
            "success_rate_pct": success_rate,
            "throughput_1m": throughput,
            "avg_profit": avg_profit,
        }

    def latency_series(self, n: int = 50) -> tuple[list[str], list[int]]:
        items = list(self.events)[-n:]
        labels = [e.timestamp.strftime("%H:%M:%S") for e in items]
        values = [e.latency_ms for e in items]
        return labels, values


async def mock_metrics_publisher(broker: SSEBroker, store: DataStore, render_html) -> None:
    """Generate mock metrics and publish pre-rendered HTML to SSE broker.

    Throughput target: ~5–20 events per minute with jitter.
    """
    # Determine a base interval with jitter to hit 5–20 events/minute (~3–12s)
    while True:
        now_dt = datetime.now(timezone.utc)
        latency = int(random.uniform(40, 450))
        ok_roll = random.random()
        status = "ok"
        err = None
        if ok_roll < 0.08:
            status = "critical"
            err = "critical: simulated failure"
        elif ok_roll < 0.20:
            status = "warning"
            err = "warning: simulated slowdown"

        profit = round(random.uniform(-0.01, 0.05), 4)  # -1% to +5%

        evt = MetricsEvent(
            timestamp=now_dt,
            bot_name=_random_bot(),
            latency_ms=latency,
            success_rate=0.0,  # computed in store kpis
            tx_hash=_random_tx_hash(),
            error=err,
            status=status,
            profit=profit,
        )
        store.add(evt)
        kpis = store.kpis()
        labels, values = store.latency_series()
        html = render_html(
            "partials/metrics.html",
            {
                "kpis": kpis,
                "latency_series": list(zip(labels, values)),
                "last_events": store.last_events(25),
            },
        )
        await broker.publish(html)

        # Sleep 3-12 seconds to simulate 5–20 events per minute
        sleep_s = random.uniform(3, 12)
        await asyncio.sleep(sleep_s)


def _shorten_tx_hash(tx: str) -> str:
    if not isinstance(tx, str) or len(tx) < 12:
        return str(tx)
    if not str(tx).startswith("0x"):
        tx = "0x" + str(tx)
    return f"{tx[:10]}...{tx[-6:]}"


def parse_silverback_json(obj: dict) -> MetricsEvent:
    # Timestamp
    if isinstance(obj.get("timestamp"), str):
        ts = datetime.fromisoformat(obj["timestamp"].replace("Z", "+00:00"))
    elif isinstance(obj.get("time"), str):
        ts = datetime.fromisoformat(obj["time"].replace("Z", "+00:00"))
    elif isinstance(obj.get("ts"), (int, float)):
        ts = datetime.fromtimestamp(float(obj["ts"]), tz=timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    bot = obj.get("bot_name") or obj.get("bot") or obj.get("name") or "silverback"

    # Latency
    latency_ms = None
    if isinstance(obj.get("latency_ms"), (int, float)):
        latency_ms = int(obj["latency_ms"])
    elif isinstance(obj.get("latency"), (int, float)):
        val = float(obj["latency"])  # seconds or ms
        latency_ms = int(val * 1000 if val < 1000 else val)
    if latency_ms is None:
        latency_ms = 0

    # Error / status
    err = obj.get("error") or obj.get("err") or obj.get("message")
    status = obj.get("status")

    # Profit (optional)
    profit = None
    if isinstance(obj.get("profit"), (int, float)):
        profit = float(obj["profit"])

    # Tx hash
    raw_tx = obj.get("tx_hash") or obj.get("hash") or obj.get("tx") or ""
    tx_hash = _shorten_tx_hash(raw_tx) if raw_tx else ""

    return MetricsEvent(
        timestamp=ts,
        bot_name=str(bot),
        latency_ms=int(latency_ms),
        success_rate=0.0,
        tx_hash=tx_hash,
        error=str(err) if err is not None else None,
        status=str(status) if status else ("ok" if not err else "critical"),
        profit=profit,
    )


async def tail_jsonl_and_broadcast(path: Path, broker: SSEBroker, store: DataStore, render_html, from_start: bool = False) -> None:
    """Tail a JSONL file and broadcast rendered HTML using the same partial as mock mode."""
    while True:
        try:
            if not path.exists():
                await asyncio.sleep(1.0)
                continue
            with path.open("r", encoding="utf-8") as f:
                if not from_start:
                    f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line == "":
                        await asyncio.sleep(0.5)
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
                    evt = parse_silverback_json(obj)
                    store.add(evt)
                    kpis = store.kpis()
                    labels, values = store.latency_series()
                    html = render_html(
                        "partials/metrics.html",
                        {
                            "kpis": kpis,
                            "latency_series": list(zip(labels, values)),
                            "last_events": store.last_events(25),
                        },
                    )
                    await broker.publish(html)
        except Exception:
            await asyncio.sleep(1.0)


