from __future__ import annotations

import asyncio
import json
import random
from collections import deque
from datetime import datetime, timezone, timedelta
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

    def throughput_series(self, minutes: int = 30) -> tuple[list[str], list[int]]:
        # Count events per minute for recent minutes present in data (up to `minutes` samples)
        counts: dict[str, int] = {}
        for e in self.events:
            key = e.timestamp.strftime("%H:%M")
            counts[key] = counts.get(key, 0) + 1
        # Sort by time using a reasonable reconstruction from keys
        keys_sorted = sorted(counts.keys())
        if len(keys_sorted) > minutes:
            keys_sorted = keys_sorted[-minutes:]
        values = [counts[k] for k in keys_sorted]
        return keys_sorted, values

    def profit_series(self, n: int = 50) -> tuple[list[str], list[float]]:
        items = list(self.events)[-n:]
        labels: list[str] = []
        values: list[float] = []
        cum = 0.0
        for e in items:
            labels.append(e.timestamp.strftime("%H:%M:%S"))
            if isinstance(e.profit, (int, float)):
                cum += float(e.profit)
            values.append(round(cum, 4))
        return labels, values

    def heatmap_matrix(self, cols: int = 12) -> dict:
        """Build a simple latency heatmap for recent time windows.

        Rows are latency buckets (ms): [0-100, 100-200, 200-300, 300+]
        Cols are 5-second windows for the last `cols`*5 seconds.
        """
        now = datetime.now(timezone.utc)
        window = timedelta(seconds=5)
        # Prepare buckets
        bucket_edges = [0, 100, 200, 300, 10**9]
        row_labels = ["0-100", "100-200", "200-300", "300+"]
        # Precompute windows
        col_starts = [now - window * (cols - i) for i in range(cols)]
        col_ends = [start + window for start in col_starts]
        # Initialize matrix
        matrix = [[0 for _ in range(cols)] for _ in range(4)]
        for e in self.events:
            # find column
            for j, (s, t) in enumerate(zip(col_starts, col_ends)):
                if s <= e.timestamp <= t:
                    # find row (bucket)
                    lat = e.latency_ms
                    for r in range(4):
                        if bucket_edges[r] <= lat < bucket_edges[r+1]:
                            matrix[r][j] += 1
                            break
                    break
        # Flatten for chart.js matrix
        cells = []
        for r in range(4):
            for c in range(cols):
                cells.append({"x": c, "y": r, "v": matrix[r][c]})
        return {"cells": cells, "rows": row_labels, "cols": cols}

    def _is_same_utc_day(self, a: datetime, b: datetime) -> bool:
        a_d = a.astimezone(timezone.utc).date()
        b_d = b.astimezone(timezone.utc).date()
        return a_d == b_d

    def daily_events(self, day: datetime | None = None) -> list[MetricsEvent]:
        ref = day or datetime.now(timezone.utc)
        return [e for e in self.events if self._is_same_utc_day(e.timestamp, ref)]

    def daily_summary(self) -> dict:
        items = self.daily_events()
        total = len(items)
        if total == 0:
            return {
                "total_events": 0,
                "avg_latency_ms": 0,
                "success_rate_pct": 0.0,
                "profit_total": 0.0,
                "status_counts": {"ok": 0, "warning": 0, "critical": 0},
                "top_bots": [],
            }
        avg_latency = sum(e.latency_ms for e in items) / total
        successes = sum(1 for e in items if not e.error and (e.status in (None, "ok")))
        success_rate = round(successes * 100.0 / total, 2)
        profit_total = round(sum(float(e.profit) for e in items if isinstance(e.profit, (int, float))), 4)
        status_counts = {"ok": 0, "warning": 0, "critical": 0}
        for e in items:
            st = e.status or ("ok" if not e.error else "critical")
            if st not in status_counts:
                status_counts[st] = 0
            status_counts[st] += 1
        bot_profit: dict[str, float] = {}
        for e in items:
            if isinstance(e.profit, (int, float)):
                bot_profit[e.bot_name] = bot_profit.get(e.bot_name, 0.0) + float(e.profit)
        top_bots = sorted(bot_profit.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return {
            "total_events": total,
            "avg_latency_ms": int(avg_latency),
            "success_rate_pct": success_rate,
            "profit_total": profit_total,
            "status_counts": status_counts,
            "top_bots": top_bots,
        }


class SensorData:
    """Simple fake sensor for temperature/humidity readings."""

    def __init__(self) -> None:
        self.min_temp = 18.0
        self.max_temp = 26.0
        self.min_humidity = 30.0
        self.max_humidity = 65.0

    def generate_reading(self) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "timestamp": now.isoformat(),
            "temperature": round(random.uniform(self.min_temp, self.max_temp), 1),
            "humidity": round(random.uniform(self.min_humidity, self.max_humidity), 1),
            "status": random.choice(["normal", "warning", "critical"]),
        }


class SensorStore:
    """In-memory fixed-size buffer of recent sensor readings."""

    def __init__(self, maxlen: int = 20) -> None:
        self.readings: Deque[dict] = deque(maxlen=maxlen)

    def add(self, reading: dict) -> None:
        self.readings.append(reading)

    def ensure_min_samples(self, sensor: "SensorData", count: int = 20) -> None:
        while len(self.readings) < count:
            self.add(sensor.generate_reading())

    def series(self) -> tuple[list[str], list[float], list[float]]:
        """Return (labels, temps, humidities). Labels are HH:MM:SS."""
        items = list(self.readings)
        labels: list[str] = []
        temps: list[float] = []
        hums: list[float] = []
        for r in items:
            try:
                ts = datetime.fromisoformat(str(r.get("timestamp")).replace("Z", "+00:00"))
            except Exception:
                ts = datetime.now(timezone.utc)
            labels.append(ts.strftime("%H:%M:%S"))
            temps.append(float(r.get("temperature", 0.0)))
            hums.append(float(r.get("humidity", 0.0)))
        return labels, temps, hums


async def mock_metrics_publisher(broker: SSEBroker, store: DataStore, render_html) -> None:
    """Generate mock metrics and publish pre-rendered HTML to SSE broker.

    Throughput target: ~5–20 events per minute with jitter.
    """
    # Determine a base interval with jitter to hit 5–20 events/minute (~3–12s)
    # Initialize fake sensors for the optional 5th view
    sensor = SensorData()
    sensor_store = SensorStore(maxlen=20)
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
        # Update sensor stream alongside metrics
        reading = sensor.generate_reading()
        sensor_store.add(reading)
        sensor_store.ensure_min_samples(sensor, 20)
        s_labels, s_temp, s_hum = sensor_store.series()
        kpis = store.kpis()
        labels, values = store.latency_series()
        thr_labels, thr_values = store.throughput_series()
        prof_labels, prof_values = store.profit_series()
        heat = store.heatmap_matrix()
        html = render_html(
            "partials/metrics.html",
            {
                "kpis": kpis,
                "latency_series": list(zip(labels, values)),
                "throughput_series": list(zip(thr_labels, thr_values)),
                "profit_series": list(zip(prof_labels, prof_values)),
                "heatmap": heat,
                "last_events": store.last_events(25),
                # Sensors view data
                "sensor_labels": s_labels,
                "sensor_temp_values": s_temp,
                "sensor_humidity_values": s_hum,
                "sensor_latest": reading,
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


def parse_bot_log_to_event(log_obj: dict) -> MetricsEvent | None:
    """Parse bot log JSON and extract metrics to create a MetricsEvent.
    
    Extracts:
    - Timestamp from log
    - Transaction hashes from messages
    - Latency from timing messages (e.g., "10.560s")
    - Status from log level
    - Bot name from message patterns
    - Fees/profit info if available
    """
    import re
    
    # Parse timestamp
    if isinstance(log_obj.get("timestamp"), str):
        ts = datetime.fromisoformat(log_obj["timestamp"].replace("Z", "+00:00"))
    elif isinstance(log_obj.get("time"), str):
        ts = datetime.fromisoformat(log_obj["time"].replace("Z", "+00:00"))
    else:
        ts = datetime.now(timezone.utc)
    
    message = str(log_obj.get("message", ""))
    level = log_obj.get("level", 20)
    
    # Extract transaction hash from message
    tx_hash = ""
    tx_pattern = r'0x[a-fA-F0-9]{64}'
    tx_matches = re.findall(tx_pattern, message)
    if tx_matches:
        tx_hash = _shorten_tx_hash(tx_matches[-1])  # Use last match (most recent)
    
    # Extract latency from timing messages (e.g., "10.560s" or "28.330s")
    latency_ms = 0
    latency_pattern = r'(\d+\.?\d*)\s*s\s*\('
    latency_match = re.search(latency_pattern, message)
    if latency_match:
        latency_seconds = float(latency_match.group(1))
        latency_ms = int(latency_seconds * 1000)
    
    # Extract bot name from message patterns
    bot_name = "bot"
    if "price[" in message.lower():
        bot_name = "price-bot"
    elif "rsi[" in message.lower():
        bot_name = "rsi-bot"
    elif "trade" in message.lower() or "perform_trade" in message.lower():
        bot_name = "trading-bot"
    elif "amount_to_sell" in message.lower():
        bot_name = "strategy-bot"
    
    # Determine status from level and message
    status = "ok"
    error = None
    if level >= 40:
        status = "critical"
        error = message[:100]  # First 100 chars
    elif level == 30:
        status = "warning"
        if "rate-limited" in message.lower():
            error = "Rate limited"
    elif level == 20:
        status = "ok"
    
    # Extract fees/profit if mentioned
    profit = None
    fee_pattern = r'total fees paid\s*=\s*(\d+)'
    fee_match = re.search(fee_pattern, message)
    if fee_match:
        # Convert fees to a small negative profit impact (for visualization)
        fees = int(fee_match.group(1))
        # Assume fees are in wei, convert to ETH and make negative
        profit = -float(fees) / 1e18 if fees > 0 else None
    
    # Only create event if we have meaningful data
    if tx_hash or latency_ms > 0 or "Confirmed" in message or "Submitted" in message:
        return MetricsEvent(
            timestamp=ts,
            bot_name=bot_name,
            latency_ms=latency_ms,
            success_rate=100.0 if status == "ok" else 0.0,
            tx_hash=tx_hash,
            error=error,
            status=status,
            profit=profit,
        )
    
    return None


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
    last_publish = 0.0
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
                        # No new line; periodically publish a keepalive update with latest aggregates
                        await asyncio.sleep(0.5)
                        now = asyncio.get_event_loop().time()
                        if now - last_publish > 5.0:
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
                            last_publish = now
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


