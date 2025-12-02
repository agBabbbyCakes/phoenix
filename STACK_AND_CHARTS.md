# Phoenix Dashboard - Technology Stack & Chart Data Ingestion

## Complete Dependencies List

### Python Backend Dependencies

#### Core Framework & Server
- **fastapi** (v0.115.0) - Modern Python web framework
- **uvicorn[standard]** (v0.30.6) - ASGI server with standard extras
- **Jinja2** (v3.1.4) - Template engine

#### Real-time & Communication
- **sse-starlette** (v2.1.3) - Server-Sent Events implementation

#### Data & Blockchain
- **web3** (≥6.0.0) - Ethereum blockchain interaction library
- **python-dotenv** (≥1.0.0) - Environment variable management
- **pydantic-settings** (≥2.0.0) - Settings management with Pydantic

#### Desktop Application
- **pywebview** (≥5.0.0) - Lightweight webview wrapper for desktop apps

#### Build & Packaging
- **pyinstaller** (≥5.13.0) - Package Python apps as standalone executables
- **python-multipart** - Required for FastAPI form data handling

#### Development Dependencies
- **ruff** - Fast Python linter
- **black** - Python code formatter

### Frontend JavaScript Libraries (CDN)

#### Core Frameworks
- **Alpine.js** (v3.x.x) - Lightweight reactive framework
  - Used across all pages for reactive UI components
  - ~15KB minified

#### HTTP & Real-time
- **HTMX** (v1.9.12) - HTML extension for dynamic content
  - Main library: `htmx.org@1.9.12`
  - SSE Extension: `htmx.org/dist/ext/sse.js`
  - Enables SSE connections and DOM updates without custom JS

#### Charting Libraries
- **Chart.js** (v4.4.1) - Canvas-based charting library
  - Primary charting engine for all visualizations
- **chartjs-plugin-zoom** (v2.0.1) - Zoom and pan functionality for Chart.js
- **chartjs-chart-matrix** (v2.0.0) - Matrix/heatmap chart type for Chart.js
- **chartjs-plugin-annotation** (v3.0.1) - Annotations plugin for Chart.js
- **charts.css** (latest) - Lightweight CSS-only charts library
  - Used for simple bar charts and sparklines

#### 3D Graphics
- **Three.js** (r128 / v0.128.0) - 3D graphics library
  - Main library: `three.min.js` (r128)
  - OrbitControls: `three@0.128.0/examples/js/controls/OrbitControls.js`
  - Used for 3D point clouds, network graphs, and financial visualizations

### Frontend CSS Frameworks

#### Utility-First CSS
- **Tailwind CSS** (CDN) - Utility-first CSS framework
  - Loaded via CDN: `cdn.tailwindcss.com`
  - Note: For production, should be built locally via npm

#### Component Library
- **DaisyUI** (v4.12.10) - Component library for Tailwind CSS
  - Provides pre-built components (buttons, cards, modals, etc.)
  - Full distribution: `daisyui@4.12.10/dist/full.min.css`

#### Typography
- **Google Fonts - Inter** - Modern sans-serif font family
  - Weights: 300, 400, 500, 600, 700
  - Loaded from: `fonts.googleapis.com`

### Custom JavaScript Modules

#### Application-Specific Scripts
Located in `/static/js/`:
- `main.js` - Main dashboard logic, chart initialization, SSE handling
- `dashboard-alpine.js` - Alpine.js state management for dashboard
- `ide-dashboard.js` - IDE dashboard specific functionality
- `bot-explorer.js` - Bot explorer page logic
- `bots-page.js` - Bots management page
- `bot-profile.js` - Individual bot profile page
- `dashboard-ui.js` - Dashboard UI utilities
- `graph3d.js` - 3D network graph visualization
- `pointcloud3d.js` - 3D point cloud visualization
- `financial3d.js` - 3D financial chart visualization
- `BotHealthTable.js` - Bot health table component

### Custom CSS Modules

Located in `/static/css/`:
- `bot-explorer.css` - Bot explorer page styles
- `glassmorphism.css` - Glass effect styling
- Additional component-specific stylesheets

### Build & Deployment Tools

#### Python Packaging
- **Briefcase** - Cross-platform desktop app packaging
  - Configured in `pyproject.toml`
  - Supports Windows, macOS, and Linux builds

#### Containerization
- **Docker** - Container support (Dockerfile present)
  - For Linux builds and deployments

### Runtime Requirements

#### Python Version
- **Python 3.11+** (recommended, though may work with 3.9+)
  - Note: Some configurations may use Python 3.9+ for compatibility

#### System Dependencies
- **Node.js/npm** (optional) - For building Tailwind CSS in production
- **WebView Runtime** - Provided by OS or bundled with pywebview
  - Windows: Edge WebView2
  - macOS: WebKit
  - Linux: WebKitGTK

---

## Technology Stack

### Backend Stack

#### Core Framework
- **FastAPI** (v0.115.0) - Modern Python web framework for building APIs
  - Handles HTTP requests, routing, and middleware
  - Provides async/await support for high-performance operations
  - Used for REST API endpoints and streaming responses

#### Server & Runtime
- **Uvicorn** (v0.30.6) - ASGI server for running FastAPI
  - Handles async request/response cycles
  - Supports WebSocket and Server-Sent Events (SSE)

#### Template Engine
- **Jinja2** (v3.1.4) - Server-side templating engine
  - Renders HTML templates with dynamic data
  - Used for initial page loads and SSE HTML updates
  - Templates located in `/templates` directory

#### Real-time Communication
- **sse-starlette** (v2.1.3) - Server-Sent Events implementation
  - Enables real-time data streaming from server to client
  - Used for live metrics updates without polling
  - Implements pub/sub pattern via `SSEBroker` class

#### Data Processing
- **Python Standard Library** - Collections, asyncio, datetime
  - `collections.deque` for efficient event buffering
  - `asyncio` for concurrent data processing
  - In-memory `DataStore` for metrics aggregation

#### Optional Dependencies
- **web3** (≥6.0.0) - Ethereum blockchain interaction
- **python-dotenv** (≥1.0.0) - Environment variable management
- **pydantic-settings** (≥2.0.0) - Settings management

### Frontend Stack

#### JavaScript Frameworks & Libraries
- **Alpine.js** (v3.x) - Lightweight reactive framework
  - Provides reactive state management
  - Used for UI interactivity (theme toggles, filters, command palette)
  - Minimal JavaScript framework (~15KB)

- **Chart.js** (v4.4.1) - Canvas-based charting library
  - Primary charting engine for line charts, heatmaps
  - Supports zoom, pan, and real-time updates
  - Used for latency, throughput, and profit visualizations

- **HTMX** - HTML extension for dynamic content
  - Enables SSE connections without custom JavaScript
  - Handles DOM updates via `hx-ext="sse"`
  - Simplifies real-time UI updates

#### Styling
- **Tailwind CSS** - Utility-first CSS framework
  - Used for responsive layouts and styling
  - Dark/light theme support
  - Glassmorphism effects via custom CSS

- **Custom CSS** - Additional styling in `/static/css/`
  - `glassmorphism.css` - Glass effect styling
  - `bot-explorer.css` - Component-specific styles

#### 3D Visualizations
- **Three.js** (via CDN) - 3D graphics library
  - Used for 3D point clouds, network graphs, financial charts
  - WebGL-based rendering

### Architecture Patterns

#### Data Flow Architecture
1. **Data Sources** → **DataStore** → **SSEBroker** → **Client**
2. **Event-Driven**: New events trigger immediate updates
3. **Pub/Sub Pattern**: SSE broker fans out updates to all connected clients

#### Storage Strategy
- **In-Memory**: `DataStore` uses `deque` with max size (default 1000 events)
- **LocalStorage**: Client-side persistence for user preferences
- **No Database**: Stateless design for scalability

---

## How Charts Ingest Information

### Overview: Complete Data Ingestion Flow

The Phoenix Dashboard ingests data through **three primary methods**, all converging into a unified pipeline that updates charts in real-time. Here's the complete flow:

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION METHODS                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Method 1: Log File Tailing          Method 2: API POST     │
│  ┌──────────────────────┐           ┌──────────────────┐   │
│  │ JSONL Log File        │           │ POST /api/logs   │   │
│  │ (SILVERBACK_LOG_PATH)│           │ JSON/JSONL body  │   │
│  └──────────┬───────────┘           └────────┬─────────┘   │
│             │                                 │              │
│             └─────────────┬───────────────────┘              │
│                           │                                  │
│                           ▼                                  │
│              ┌─────────────────────────┐                     │
│              │   Parse & Extract       │                     │
│              │   - Timestamp            │                     │
│              │   - Bot Name             │                     │
│              │   - Latency (ms)         │                     │
│              │   - Status/Error          │                     │
│              │   - Transaction Hash      │                     │
│              │   - Profit               │                     │
│              └──────────┬────────────────┘                    │
│                         │                                     │
│                         ▼                                     │
│              ┌─────────────────────────┐                     │
│              │   Create MetricsEvent   │                     │
│              │   (Pydantic Model)       │                     │
│              └──────────┬────────────────┘                    │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │   DataStore.add(event)   │
              │   (In-Memory Buffer)     │
              │   - Circular deque        │
              │   - Max 1000 events       │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   Aggregate Metrics     │
              │   - Calculate KPIs      │
              │   - Build time series    │
              │   - Generate heatmap    │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   Render HTML Partial   │
              │   (Jinja2 Template)     │
              │   - KPIs                │
              │   - Chart data          │
              │   - Event table         │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   SSEBroker.publish()   │
              │   (Pub/Sub Queue)       │
              │   - Fan out to clients  │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   SSE Stream (/stream)  │
              │   - EventSourceResponse │
              │   - Keepalive pings     │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   Client (HTMX)         │
              │   - Receives HTML        │
              │   - Swaps DOM            │
              └──────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │   Chart.js Update       │
              │   - Extract data         │
              │   - Update datasets      │
              │   - Render charts         │
              └─────────────────────────┘
```

### Step-by-Step: How Data Gets Ingested

#### Step 1: Data Arrives (Three Entry Points)

**A. Log File Tailing (Production Mode)**
```python
# app/main.py - Startup
log_path = settings.silverback_log_path
if log_path and not settings.force_sample:
    # Start background task
    tail_jsonl_and_broadcast(Path(log_path), broker, store, render_html)
```

**What happens:**
1. Application starts and checks for `SILVERBACK_LOG_PATH` environment variable
2. If found, starts `tail_jsonl_and_broadcast()` as background async task
3. Opens log file and seeks to end (tail mode)
4. Continuously reads new lines as they're written to file
5. Each new line = one JSON object (JSONL format)

**Example log line:**
```json
{"timestamp":"2025-01-15T10:30:45Z","bot_name":"arb-scout","latency_ms":234,"status":"ok","tx_hash":"0xabc123..."}
```

**B. HTTP API Endpoint (Programmatic Ingestion)**
```python
# POST /api/logs
# Accepts JSON or JSONL in request body
```

**What happens:**
1. Bot or external service sends POST request to `/api/logs`
2. Request body contains JSON array or JSONL (newline-delimited)
3. Server parses each JSON object
4. Extracts metrics using `parse_bot_log_to_event()`

**Example request:**
```bash
curl -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2025-01-15T10:30:45Z","bot_name":"mev-watch","latency_ms":156}'
```

**C. Mock Data Generation (Demo Mode)**
```python
# app/main.py - Startup (fallback)
if not log_path or settings.force_sample:
    mock_metrics_publisher(broker, store, render_html)
```

**What happens:**
1. Runs when no log file is configured
2. Generates random metrics every 3-12 seconds
3. Creates realistic bot events for demonstration
4. Same processing pipeline as real data

#### Step 2: Parse & Extract Metrics

**Location**: `app/data.py` → `parse_silverback_json()` or `parse_bot_log_to_event()`

**Extraction Process:**
```python
# Example: Parsing a log entry
log_obj = {
    "timestamp": "2025-01-15T10:30:45Z",
    "bot_name": "arb-scout",
    "latency_ms": 234,
    "status": "ok",
    "tx_hash": "0xabc123...",
    "profit": 0.0012
}

# Convert to MetricsEvent
event = MetricsEvent(
    timestamp=datetime.fromisoformat(log_obj["timestamp"]),
    bot_name=log_obj["bot_name"],
    latency_ms=log_obj["latency_ms"],
    status=log_obj["status"],
    tx_hash=log_obj["tx_hash"],
    profit=log_obj.get("profit"),
    error=None
)
```

**What gets extracted:**
- **Timestamp**: ISO format → Python datetime
- **Bot Name**: String identifier
- **Latency**: Milliseconds (int)
- **Status**: "ok", "warning", "critical"
- **Error**: Error message if status != "ok"
- **Transaction Hash**: Ethereum transaction ID
- **Profit**: Float value (optional)

#### Step 3: Store in DataStore

**Location**: `app/data.py` → `DataStore.add()`

```python
# DataStore maintains circular buffer
store.add(event)  # Adds to deque(maxlen=1000)
```

**What happens:**
1. Event added to `collections.deque` (circular buffer)
2. If buffer is full (1000 events), oldest event is automatically removed
3. Event is now available for aggregation queries

**Data Structure:**
```python
class DataStore:
    def __init__(self, max_events: int = 1000):
        self.events: Deque[MetricsEvent] = deque(maxlen=max_events)
```

#### Step 4: Aggregate Metrics

**Location**: `app/data.py` → Various aggregation methods

**When aggregation happens:**
- Immediately after adding event (for SSE broadcast)
- On-demand when client requests data
- Periodically for keepalive updates (every 5 seconds if no new events)

**Aggregation methods called:**
```python
kpis = store.kpis()                    # Average latency, success rate, throughput
labels, values = store.latency_series() # Last 50 latency points
thr_labels, thr_values = store.throughput_series()  # Events per minute
prof_labels, prof_values = store.profit_series()   # Cumulative profit
heat = store.heatmap_matrix()          # Latency distribution heatmap
```

**Example KPI calculation:**
```python
# Calculate average latency from all events
avg_latency = sum(e.latency_ms for e in events) / len(events)

# Calculate success rate (last 60 seconds)
last_minute = [e for e in events if e.timestamp > cutoff]
success_rate = (successes / total) * 100.0
```

#### Step 5: Render HTML Partial

**Location**: `templates/partials/metrics.html` (Jinja2 template)

**What happens:**
1. Server renders HTML template with aggregated data
2. Includes:
   - KPI cards (latency, success rate, throughput)
   - Chart data as JSON in data attributes
   - Recent events table rows
   - Heatmap data

**Example rendered HTML:**
```html
<div data-latency-labels='["10:30:00","10:30:05",...]'
     data-latency-values='[234,156,189,...]'>
  <!-- KPI cards, charts, tables -->
</div>
```

#### Step 6: Publish via SSE Broker

**Location**: `app/sse.py` → `SSEBroker.publish()`

**What happens:**
1. Rendered HTML is published to broker
2. Broker fans out to all connected client queues
3. Each client receives HTML in their dedicated queue

**Pub/Sub Pattern:**
```python
# Publisher (data source)
await broker.publish(html)

# Subscribers (connected clients)
queue = await broker.subscribe()
msg = await queue.get()  # Receives HTML
```

#### Step 7: Stream to Clients

**Location**: `app/main.py` → `GET /stream` endpoint

**What happens:**
1. Client connects via EventSource API
2. Server creates SSE stream
3. Yields HTML as SSE event:
   ```
   event: metrics_update
   data: <html>...</html>
   ```
4. Client receives via HTMX SSE extension

**SSE Format:**
```
event: metrics_update
data: <div>...</div>

event: ping
data: keepalive
```

#### Step 8: Client Updates Charts

**Location**: `static/js/main.js` + HTMX

**What happens:**
1. HTMX receives SSE event
2. Swaps innerHTML of target element
3. JavaScript detects DOM change
4. Extracts chart data from data attributes
5. Updates Chart.js datasets:
   ```javascript
   chart.data.labels.push(newTimestamp);
   chart.data.datasets[0].data.push(newValue);
   chart.update('none'); // No animation for real-time
   ```

### 1. Data Ingestion Methods (Detailed)

#### A. Real-time Log File Tailing
**Location**: `app/data.py` → `tail_jsonl_and_broadcast()`

- **Input**: JSONL (JSON Lines) log file
- **Process**:
  1. Tails log file continuously (reads new lines as they're written)
  2. Parses each JSON line using `parse_silverback_json()`
  3. Extracts metrics: timestamp, bot_name, latency_ms, status, profit, tx_hash
  4. Creates `MetricsEvent` objects
  5. Adds to `DataStore`
  6. Renders HTML partial and publishes via SSE

- **Configuration**: Set `SILVERBACK_LOG_PATH` environment variable

#### B. Mock Data Generation
**Location**: `app/data.py` → `mock_metrics_publisher()`

- **Purpose**: Demo mode when no real log file exists
- **Process**:
  1. Generates random metrics every 3-12 seconds
  2. Creates realistic bot events (arb-scout, mev-watch, etc.)
  3. Simulates latency spikes, errors, and success rates
  4. Includes profit calculations
  5. Publishes via SSE same as real data

#### C. API Endpoint Ingestion
**Location**: `app/main.py` → `/api/logs` (POST)

- **Input**: JSON or JSONL in request body
- **Process**:
  1. Accepts POST requests with log data
  2. Parses JSON/JSONL format
  3. Converts to `MetricsEvent` via `parse_bot_log_to_event()`
  4. Adds to `DataStore`
  5. Triggers metrics update broadcast

### 2. Data Processing & Aggregation

#### DataStore Class (`app/data.py`)

The `DataStore` maintains an in-memory buffer of recent events and provides aggregation methods:

**Key Methods**:
- `add(event)` - Adds new event to circular buffer (max 1000 events)
- `kpis()` - Calculates KPIs:
  - Average latency (ms)
  - Success rate (%)
  - Throughput (events/minute)
  - Average profit
- `latency_series(n=50)` - Returns last N latency values with timestamps
- `throughput_series(minutes=30)` - Counts events per minute
- `profit_series(n=50)` - Cumulative profit over time
- `heatmap_matrix(cols=12)` - Latency distribution heatmap data

**Data Structure**:
```python
events: Deque[MetricsEvent]  # Circular buffer, maxlen=1000
```

### 3. Real-time Broadcasting (SSE)

#### SSEBroker (`app/sse.py`)

**Architecture**:
- Pub/Sub pattern with asyncio queues
- Each client gets a dedicated queue
- Publisher fans out messages to all subscribers
- Queue size limit (100) prevents memory issues)

**Flow**:
1. Client connects to `/stream` endpoint
2. Server creates queue and subscribes client
3. Data publisher calls `broker.publish(html)`
4. HTML is queued for all subscribers
5. SSE stream yields `{"event": "metrics_update", "data": html}`
6. Client receives update via HTMX SSE extension

**Endpoint**: `GET /stream`
- Returns `EventSourceResponse` (SSE stream)
- Sends keepalive pings every 15 seconds
- Handles client disconnections gracefully

### 4. Client-Side Chart Updates

#### Method 1: HTMX SSE (Primary Method)

**Location**: `templates/ide-dashboard.html`, `templates/dashboard.html`

```html
<div id="metrics-panel" 
     hx-ext="sse" 
     sse-connect="/stream" 
     sse-swap="metrics_update" 
     hx-swap="innerHTML">
  {{ initial_metrics_html | safe }}
</div>
```

**How it works**:
1. HTMX connects to `/stream` via EventSource API
2. Listens for `metrics_update` events
3. Receives pre-rendered HTML from server
4. Swaps innerHTML of target element
5. JavaScript detects DOM changes and updates Chart.js

**Advantages**:
- Server pre-renders HTML (reduces client processing)
- Automatic reconnection on disconnect
- No custom JavaScript needed for SSE connection

#### Method 2: REST API Polling (Fallback)

**Location**: `static/js/main.js` → `loadChart()`

```javascript
const endpoint = `/api/live/${currentMetric}`;
const res = await fetch(endpoint);
const data = await res.json();
// Update Chart.js with new data
```

**Endpoints**:
- `GET /api/live/latency` - Returns `{timestamps: [], values: []}`
- `GET /api/live/throughput` - Event counts over time
- `GET /api/live/profit` - Profit values
- `GET /api/live/success_rate` - Success percentages

**Polling Interval**: ~2-5 seconds (configurable)

#### Method 3: Chart.js Direct Updates

**Location**: `static/js/main.js`

**Update Process**:
1. Receive new data (via SSE HTML swap or API poll)
2. Extract data from DOM attributes or JSON response
3. Update Chart.js dataset:
   ```javascript
   chart.data.labels.push(newTimestamp);
   chart.data.datasets[0].data.push(newValue);
   // Maintain max data points (e.g., last 50)
   if (chart.data.labels.length > 50) {
     chart.data.labels.shift();
     chart.data.datasets[0].data.shift();
   }
   chart.update('none'); // 'none' = no animation for real-time
   ```

### 5. Chart Types & Data Formats

#### Line Charts (Latency, Throughput, Profit)
- **Library**: Chart.js
- **Data Format**: `{labels: ["HH:MM:SS", ...], values: [123, 456, ...]}`
- **Update**: Append new point, remove oldest if > max points
- **Features**: Zoom, pan, moving average overlay

#### Heatmap (Latency Distribution)
- **Library**: Chart.js with matrix data
- **Data Format**: 
  ```javascript
  {
    cells: [{x: 0, y: 0, v: 5}, ...],  // x=time window, y=latency bucket, v=count
    rows: ["0-100ms", "100-200ms", "200-300ms", "300+ms"],
    cols: 12  // 12 time windows of 5 seconds each
  }
  ```
- **Update**: Recalculate entire matrix from DataStore events

#### 3D Visualizations
- **Library**: Three.js
- **Data Source**: `GET /api/charts/data`
- **Format**: Array of event objects with all metrics
- **Types**: Point cloud, network graph, financial 3D

#### Chart Annotations (Interactive)
- **Library**: Chart.js + Alpine.js
- **Data**: Stored in browser localStorage
- **Features**: Markers, lines, regions, text notes
- **Interaction**: Click on chart to add annotations

### 6. Initial Data Loading

**Server-Side Rendering** (First Load):
1. On page load, server queries `DataStore` for current state
2. Renders `partials/metrics.html` with initial data
3. Includes:
   - KPI values
   - Last 50 latency points
   - Last 30 throughput samples
   - Recent events table
4. Client receives complete HTML with data embedded in DOM

**Data Attributes** (for JavaScript extraction):
```html
<div data-latency-labels='["10:00:00", ...]'
     data-latency-values='[123, 456, ...]'
     data-throughput-labels='...'
     data-throughput-values='...'>
```

### 7. Performance Optimizations

1. **Circular Buffer**: `DataStore` uses `deque(maxlen=1000)` to limit memory
2. **Pre-rendered HTML**: Server renders HTML, reducing client CPU
3. **Incremental Updates**: Charts append new points, don't redraw entire dataset
4. **Queue Size Limits**: SSE queues capped at 100 messages (drops for slow clients)
5. **Lazy Chart Initialization**: Charts only initialize when container is visible
6. **Update Throttling**: Chart updates use `update('none')` to skip animations

### 8. Error Handling & Fallbacks

- **SSE Disconnect**: HTMX automatically reconnects
- **API Failure**: Falls back to dummy data mode (if `USE_DUMMY_DATA` flag set)
- **Missing Data**: Charts show empty state gracefully
- **File Tailing Errors**: Falls back to mock data publisher
- **JSON Parse Errors**: Logged and skipped, doesn't crash pipeline

---

## Summary

The Phoenix Dashboard uses a **modern async Python backend** (FastAPI + SSE) with a **lightweight JavaScript frontend** (Alpine.js + Chart.js + HTMX). Charts ingest data through:

1. **Real-time streaming** via Server-Sent Events (primary)
2. **REST API polling** as fallback
3. **Server-side HTML rendering** for efficient updates

The architecture is **event-driven**, **stateless**, and **scalable**, with in-memory buffering and efficient pub/sub broadcasting to multiple clients simultaneously.

---

## Quick Reference: Dependency Summary

### Backend Dependencies (Python)
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.0 | Web framework |
| uvicorn[standard] | 0.30.6 | ASGI server |
| Jinja2 | 3.1.4 | Template engine |
| sse-starlette | 2.1.3 | SSE implementation |
| web3 | ≥6.0.0 | Blockchain interaction |
| python-dotenv | ≥1.0.0 | Environment variables |
| pydantic-settings | ≥2.0.0 | Settings management |
| pywebview | ≥5.0.0 | Desktop webview |
| pyinstaller | ≥5.13.0 | Executable packaging |
| python-multipart | latest | Form data handling |

### Frontend Dependencies (CDN)
| Library | Version | Purpose |
|---------|---------|---------|
| Alpine.js | 3.x.x | Reactive framework |
| HTMX | 1.9.12 | Dynamic HTML |
| Chart.js | 4.4.1 | Charting library |
| chartjs-plugin-zoom | 2.0.1 | Zoom/pan for charts |
| chartjs-chart-matrix | 2.0.0 | Heatmap charts |
| chartjs-plugin-annotation | 3.0.1 | Chart annotations |
| charts.css | latest | CSS-only charts |
| Three.js | r128 | 3D graphics |
| Tailwind CSS | CDN | Utility CSS |
| DaisyUI | 4.12.10 | Component library |
| Inter Font | - | Typography |

### Total Dependency Count
- **Python packages**: 10 core + 2 dev dependencies
- **Frontend CDN libraries**: 11 JavaScript + 3 CSS
- **Custom modules**: 11 JavaScript files + 2+ CSS files
- **Build tools**: Briefcase, Docker, PyInstaller

---

## CSS Charts: Usage & Implementation

The Phoenix Dashboard uses **two types of CSS-only charts** for lightweight, performant visualizations that don't require JavaScript charting libraries.

### 1. Charts.css Library (Third-Party)

**Library**: `charts.css` (loaded from CDN)  
**Purpose**: Pure CSS chart library using HTML tables with CSS variables  
**Use Cases**: Streaming data tables, simple bar/column charts

#### Implementation Example

**Location**: `templates/demo.html`, `templates/dashboard.html`

```html
<!-- Streaming column chart using Charts.css -->
<table class="charts-css column show-primary-axis show-data-axes">
  <thead>
    <tr>
      <th>Time</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody id="live-chart-body">
    <!-- Rows streamed via HTMX -->
  </tbody>
</table>
```

**How it works:**
1. Server streams HTML table rows via SSE/HTMX
2. Each row uses `data-c` attribute for value:
   ```html
   <tr>
     <td>10:30:00</td>
     <td data-c="75">75</td>  <!-- Charts.css reads data-c for height -->
   </tr>
   ```
3. Charts.css automatically styles based on `data-c` values
4. No JavaScript needed - pure CSS rendering

**Streaming Pattern** (`app/main.py`):
```python
@app.get("/silverback/streaming-demo/chart-stream")
async def chart_stream(request: Request):
    async def stream():
        while True:
            val = random.randint(0, 100)
            # Stream new row
            yield f'<tr><td>{timestamp}</td><td data-c="{val}">{val}</td></tr>\n'
            await asyncio.sleep(1.0)
```

**Advantages:**
- ✅ Zero JavaScript overhead
- ✅ Works with streaming HTML (HTMX SSE)
- ✅ Accessible (semantic HTML tables)
- ✅ Lightweight (~10KB CSS)

**Limitations:**
- ❌ Limited chart types (bar, column, area, line)
- ❌ No interactivity (zoom, pan, tooltips)
- ❌ Less customization than Chart.js

### 2. Custom CSS Charts (Built-in)

**Location**: `static/css/charts.css`  
**Purpose**: Custom lightweight charts for specific use cases  
**Types**: Sparklines, horizontal bars, status rings, heatmaps

#### A. Sparklines (Mini Line Charts)

**Usage**: Real-time latency trends in sidebars/logs

```html
<!-- Component: templates/components/css_sparkline.html -->
<div class="css-sparkline" aria-hidden="true">
  <i></i><i></i><i></i>  <!-- 30 bars -->
</div>
```

**Update via JavaScript** (`static/js/main.js`):
```javascript
// Update sparkline values
const spark = document.querySelector('.css-sparkline');
const bars = spark.querySelectorAll('i');
bars.forEach((bar, idx) => {
  const value = normalizedLatency[idx]; // 0..1
  bar.style.setProperty('--v', value);  // CSS variable
});
```

**CSS Implementation**:
```css
.css-sparkline i {
  --v: 0;  /* Value from 0 to 1 */
  width: 3px;
  height: calc(var(--v) * 100%);
  background: rgba(99, 102, 241, 0.9);
}
```

#### B. Horizontal Progress Bars

**Usage**: Single metric indicators (latency, success rate)

```html
<div class="css-bar" style="--value: 0.75"></div>
```

**CSS Implementation**:
```css
.css-bar {
  --value: 0.0;  /* 0 to 1 */
  height: 8px;
  background: rgba(255,255,255,0.06);
}
.css-bar::before {
  width: calc(var(--value) * 100%);
  background: linear-gradient(90deg, #22d3ee, #60a5fa);
}
```

#### C. Status Ring (Donut Chart)

**Usage**: Health distribution visualization

```html
<!-- Component: templates/components/css_status_ring.html -->
<div class="css-status-ring" 
     style="--ok: 60; --slow: 30; --err: 10;"></div>
```

**CSS Implementation** (Conic Gradient):
```css
.css-status-ring {
  background: conic-gradient(
    #10b981 0% calc(var(--ok) * 1%),
    #f59e0b calc(var(--ok) * 1%) calc((var(--ok) + var(--slow)) * 1%),
    #ef4444 calc((var(--ok) + var(--slow)) * 1%) 100%
  );
  /* Mask creates donut shape */
  mask: radial-gradient(farthest-side, transparent 55%, black 56%);
}
```

**Update Pattern**:
```javascript
// Update status ring from metrics
const ring = document.querySelector('.css-status-ring');
ring.style.setProperty('--ok', '60');
ring.style.setProperty('--slow', '30');
ring.style.setProperty('--err', '10');
```

#### D. Heatmap Grid

**Usage**: Latency distribution over time

```html
<!-- Component: templates/components/css_heatmap.html -->
<div class="css-heatmap" style="--cols: 12;">
  <i style="--val: 0.5"></i>  <!-- 48 cells -->
  <i style="--val: 0.8"></i>
  <!-- ... -->
</div>
```

**CSS Implementation**:
```css
.css-heatmap {
  --cols: 12;
  display: grid;
  grid-template-columns: repeat(var(--cols), 1fr);
  gap: 4px;
}
.css-heatmap i {
  --val: 0.0;  /* 0 to 1 */
  aspect-ratio: 1 / 1;
  background: rgba(34, 211, 238, var(--val));
}
```

### When to Use CSS Charts vs Chart.js

#### Use CSS Charts For:
- ✅ **Sparklines** in sidebars/headers (lightweight, always visible)
- ✅ **Status indicators** (single values, progress bars)
- ✅ **Streaming tables** (Charts.css with HTMX)
- ✅ **Mini charts** in compact spaces
- ✅ **Performance-critical** areas (no JS overhead)
- ✅ **Accessibility** (semantic HTML)

#### Use Chart.js For:
- ✅ **Main dashboard charts** (interactive, zoomable)
- ✅ **Complex visualizations** (heatmaps, 3D, annotations)
- ✅ **User interactions** (hover tooltips, click events)
- ✅ **Multiple datasets** (overlays, comparisons)
- ✅ **Time series** with many data points

### CSS Charts Data Flow

```
┌─────────────────────────────────────────┐
│         Data Source (SSE/API)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Extract Value (JavaScript)         │
│      - Normalize to 0..1 range          │
│      - Update CSS variable              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      CSS Variable Update                │
│      element.style.setProperty('--v', value)│
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      CSS Renders Chart                 │
│      - calc(var(--v) * 100%)           │
│      - Background gradients            │
│      - Grid layouts                     │
└─────────────────────────────────────────┘
```

### Example: Real-Time Sparkline Update

**Complete Flow** (`static/js/main.js`):

```javascript
// 1. Receive metrics event via SSE
window.handleMetrics = function(detail) {
  const evt = JSON.parse(detail);
  const latency = evt.latency_ms;
  
  // 2. Normalize latency (0-500ms → 0-1)
  const normLatency = Math.min(latency / 500, 1.0);
  
  // 3. Add to buffer
  sparklineVals.push(normLatency);
  if (sparklineVals.length > 30) sparklineVals.shift();
  
  // 4. Update CSS variables
  const spark = document.querySelector('.css-sparkline');
  const bars = spark.querySelectorAll('i');
  bars.forEach((bar, idx) => {
    const v = sparklineVals[idx] ?? 0;
    bar.style.setProperty('--v', v);  // CSS reads this
  });
};
```

**Result**: Smooth, real-time sparkline with zero Chart.js overhead.

### Performance Benefits

**CSS Charts Advantages:**
- **No JavaScript execution** for rendering
- **GPU-accelerated** CSS transforms
- **Minimal DOM updates** (just CSS variables)
- **Smaller bundle size** (no chart library)
- **Faster initial render** (no JS initialization)

**Comparison:**
- Chart.js: ~200KB + initialization time
- CSS Charts: ~5KB CSS + instant render
- **Use CSS for simple, always-visible indicators**
- **Use Chart.js for complex, interactive visualizations**

### Summary

The Phoenix Dashboard uses a **hybrid approach**:
- **CSS Charts** for lightweight, always-on indicators (sparklines, status rings, mini charts)
- **Chart.js** for main dashboard visualizations (interactive, zoomable, feature-rich)
- **Charts.css** for streaming table-based charts (HTMX integration)

This provides the best of both worlds: **performance** where it matters, **rich interactivity** where needed.

