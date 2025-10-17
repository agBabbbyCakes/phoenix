# Ethereum Bot Monitoring Dashboard (phoenix)

FastAPI + SSE + HTMX + Tailwind/DaisyUI + Chart.js dashboard for real-time Ethereum bot metrics.

## Quickstart (uv)

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` in your browser.

## Features

- FastAPI backend with SSE stream at `/stream`
- HTMX SSE frontend for live updates (no WebSockets)
- Tailwind CSS + DaisyUI components for clean UI
- Chart.js latency line chart
- Live success rate, throughput per-minute, and event log

## Project Structure

```
app/
  __init__.py
  main.py           # FastAPI entrypoint
  sse.py            # SSE broker and client stream
  data.py           # in-memory store & mock generator
  models.py         # Pydantic models (metrics payload)
templates/
  base.html
  index.html
  partials/
    metrics.html
    logs.html
static/
  js/
    main.js         # Frontend logic: charts, metrics, log updates
  css/
    .gitkeep
pyproject.toml
README.md
```

## SSE Contract

- Event name used by the app: `metrics_update` (SSE sends server-rendered HTML partials)
  - HTMX replaces `#metrics-panel` innerHTML via `sse-swap="metrics_update"`.
  - The HTML partial includes data-* for charts and renders KPIs + recent events.

## Notes

- Uses `sse-starlette` via `EventSourceResponse` to send events every 2 seconds.
- HTMX SSE extension listens and dispatches `sse:metrics` events to the page.
- No WebSockets used per requirement.

## Silverback Integration & Sample Mode

This service can tail a Silverback Recorder JSON Lines file and broadcast real metrics to all connected SSE clients.

Configure via environment variables:

- `SILVERBACK_LOG_PATH`: absolute path to the JSONL file written by Silverback Recorder.
- If not set, the app automatically starts in Sample Mode (mock generator with realistic jitter and statuses). A "Sample Mode" badge appears in the header.

Run example:

```bash
SILVERBACK_JSONL_PATH=/var/log/silverback/recorder.jsonl \
uvicorn app.main:app --reload --port 8000
```

## Dev Commands

- Run dev server: `uv run uvicorn app.main:app --reload --port 8000`
- Lint: `uv run ruff check .`
- Format: `uv run black .`

## Demo/Sample Mode

To force demo data (no external dependencies), set `FORCE_SAMPLE=1`.

```bash
FORCE_SAMPLE=1 uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The dashboard will continuously stream mock metrics and sensor readings.

Health endpoint: `/health` returns `{ "status": "ok" }`.

## Container Image

Build a production image:

```bash
docker build -t botscope:latest .
docker run -p 8000:8000 -e FORCE_SAMPLE=1 botscope:latest
```

## Deploy to Render

Create `render.yaml` and deploy from Git. The service will expose port 8000, run uvicorn, and can be configured with `FORCE_SAMPLE=1` for a live demo.

Environment variables:

- `FORCE_SAMPLE`: `1` to always run demo stream.
- `SILVERBACK_LOG_PATH`: absolute path of JSONL to tail (optional).


Expected JSONL fields (flexible names are handled):

- timestamp: `timestamp` | `time` | `ts`
- bot name: `bot_name` | `bot` | `name`
- latency: `latency_ms` (ms) or `latency` (s or ms)
- success flag: `success` | `ok`
- transaction hash: `tx_hash` | `hash` | `tx`

Computed and broadcast payload:

```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "bot_name": "arb-scout",
  "latency_ms": 123,
  "success_rate": 98.5,
  "tx_hash": "0xabc12345...def789"
}
```

Notes:

- Success rate is calculated over a rolling 60-second window of tailed events.
- File rotation/truncation is detected and the tailer will reopen the file.

## Changelog

- feat: scaffolded FastAPI app with `app/main.py` and SSE `/stream`
- feat: added Jinja2 `templates/index.html` with HTMX SSE, Chart.js, Tailwind + DaisyUI
- feat: added `static/js/main.js` updating chart, success rate, throughput, and log table
- chore: added `requirements.txt` with FastAPI, uvicorn, Jinja2, sse-starlette
- docs: updated README with quickstart, structure, SSE contract, and changelog
- feat: added Silverback JSONL tailer and SSE broadcaster; env var configuration
- build: migrated to uv + pyproject.toml; added dev tools (ruff, black)
- refactor: modularized app into `app/sse.py`, `app/data.py`, `app/models.py`
- feat: templating split into `base.html` and partials
- feat: SSE streams server-rendered HTML partials (`metrics_update`) for HTMX
- feat: Sample Mode auto-enabled without `SILVERBACK_LOG_PATH`, with warning/critical statuses and profit
- ui: CMYK-inspired theme + Inter font; header cyan; KPI styling; error badges black/yellow
