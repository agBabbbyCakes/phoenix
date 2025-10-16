# Ethereum Bot Monitoring Dashboard (phoenix)

FastAPI + SSE + HTMX + Tailwind/DaisyUI + Chart.js dashboard for real-time Ethereum bot metrics.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
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
  main.py           # FastAPI entrypoint + SSE stream
templates/
  index.html        # Jinja2 template using HTMX, Tailwind, DaisyUI, Chart.js
static/
  js/
    main.js         # Frontend logic: charts, metrics, log updates
requirements.txt
README.md
```

## SSE Contract

SSE event name: `metrics`, payload JSON:

```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "bot_name": "arb-scout",
  "latency_ms": 123,
  "success_rate": 98.5,
  "tx_hash": "0xabc12345...def789"
}
```

## Notes

- Uses `sse-starlette` via `EventSourceResponse` to send events every 2 seconds.
- HTMX SSE extension listens and dispatches `sse:metrics` events to the page.
- No WebSockets used per requirement.

## Silverback Integration

This service can tail a Silverback Recorder JSON Lines file and broadcast real metrics to all connected SSE clients.

Configure via environment variables:

- `SILVERBACK_JSONL_PATH`: absolute path to the JSONL file written by Silverback Recorder.
- `SILVERBACK_TAIL_FROM_START` (optional): `true|false` (default `false`). If `true`, reads from the beginning of the file; otherwise starts at the end.

Run example:

```bash
SILVERBACK_JSONL_PATH=/var/log/silverback/recorder.jsonl \
uvicorn app.main:app --reload --port 8000
```

## Run Script (recommended)

The `scripts/run.sh` script will create a venv, install dependencies, load `.env` if present, and start the server.

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

Use environment variables in `.env` to configure:

```
PORT=8000
SILVERBACK_JSONL_PATH=/absolute/path/to/recorder.jsonl
SILVERBACK_TAIL_FROM_START=false
```

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
- chore: added scripts/run.sh with venv, install, and server bootstrap
- feat: frontend updates: bot name in header, throughput chart, error badges
