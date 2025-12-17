"""API endpoints for JSON data."""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.dependencies import get_store, get_broker
from app.data import parse_bot_log_to_event

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


@router.get("/api/bots/status")
async def get_bots_status(request: Request) -> JSONResponse:
    """Get aggregated health status for all bots.
    
    Returns bot name, last heartbeat, success ratio, failure count, 
    last block, and latency for each bot.
    """
    store = get_store(request)
    
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
        stats["total_count"] += 1
        stats["last_heartbeat"] = event.timestamp.isoformat()
        stats["latencies"].append(event.latency_ms)
        
        if event.error is None and event.status in (None, "ok"):
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1
    
    # Calculate success ratio and average latency for each bot
    bots = []
    for bot_name, stats in bot_stats.items():
        success_ratio = (stats["success_count"] / stats["total_count"] * 100) if stats["total_count"] > 0 else 0.0
        avg_latency = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
        
        bots.append({
            "bot_name": bot_name,
            "name": bot_name,  # Alias for compatibility
            "last_heartbeat": stats["last_heartbeat"],
            "success_ratio": round(success_ratio, 2),
            "success_rate": round(success_ratio, 2),  # Alias
            "failure_count": stats["failure_count"],
            "latency_ms": round(avg_latency, 2),
            "avg_latency": round(avg_latency, 2),  # Alias
            "last_block": stats["last_block"],
        })
    
    # Sort by last heartbeat (most recent first)
    bots.sort(key=lambda x: x["last_heartbeat"] or "", reverse=True)
    
    return JSONResponse({
        "status": "success",
        "bots": bots,
        "count": len(bots)
    })


@router.get("/api/charts/data")
async def get_charts_data(request: Request) -> JSONResponse:
    """Get chart data in JSON format for 3D visualizations.
    
    Returns recent events with all metrics for chart rendering.
    """
    store = get_store(request)
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


@router.post("/api/logs")
async def receive_bot_logs(request: Request) -> JSONResponse:
    """API endpoint to receive live JSON log data from bots.
    
    Accepts JSONL (newline-delimited JSON) in request body.
    Extracts metrics and updates dashboard in real-time.
    """
    store = get_store(request)
    broker = get_broker(request)
    
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


@router.get("/api/live/{metric}")
async def get_live_metric(request: Request, metric: str) -> JSONResponse:
    """Get live metric data for charts.
    
    Supported metrics: latency, throughput, profit, success_rate
    Returns: { timestamps: [...], values: [...] }
    """
    store = get_store(request)
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


@router.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204)

