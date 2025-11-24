(() => {
  // Developer toggle: renders dummy data when backend endpoints are not ready.
  // When true, chart and sidebar pollers will use random data but keep the same code paths.
  const USE_DUMMY_DATA = false;
  const connIndicator = () => document.getElementById("conn-status");
  const sampleModeBadge = () => document.getElementById("sample-mode-ind");
  const successRateEl = () => document.getElementById("successRateValue");
  const throughputEl = () => document.getElementById("throughputValue");
  const logTableBody = () => document.getElementById("logTableBody");
  const botNameEl = () => document.getElementById("botName");

  let latencyChart;
  let throughputChart;
  const maxPoints = 30;
  const eventTimes = [];
  let userPrefs = { enableMA: false, enableTrend: false, alertLatencyMs: null };

  function initCharts() {
    const ctx = document.getElementById("latencyChart");
    latencyChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Latency (ms)",
            data: [],
            borderColor: "#00bfff",
            backgroundColor: "rgba(0,191,255,0.15)",
            borderWidth: 2,
            tension: 0.25,
            pointRadius: 2,
          },
          {
            label: "MA(5)",
            data: [],
            borderColor: "#00ff88",
            backgroundColor: "rgba(0,255,136,0.1)",
            borderWidth: 1,
            tension: 0.25,
            pointRadius: 0,
            hidden: true,
          }
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: false } },
          y: { beginAtZero: true },
        },
        plugins: {
          legend: { display: false },
          zoom: {
            pan: { enabled: true, mode: 'x' },
            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed.y;
                const ds = ctx.datasetIndex === 0 ? ctx.dataset.data : [];
                let delta = '';
                if (ctx.datasetIndex === 0 && ctx.dataIndex > 0) {
                  const prev = ds[ctx.dataIndex - 1];
                  if (typeof prev === 'number') {
                    const diff = val - prev;
                    delta = ` (${diff >= 0 ? '+' : ''}${diff.toFixed(1)})`;
                  }
                }
                return `${ctx.dataset.label}: ${val}${delta}`;
              }
            }
          }
        },
      },
    });

    const tctx = document.getElementById("throughputChart");
    throughputChart = new Chart(tctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Throughput (events/min)",
            data: [],
            borderColor: "#00ff88",
            backgroundColor: "rgba(0,255,136,0.15)",
            borderWidth: 2,
            tension: 0.25,
            pointRadius: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: false } },
          y: { beginAtZero: true },
        },
        plugins: { legend: { display: false }, zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' } } },
      },
    });
  }

  function updateChart(timestampIso, latencyMs) {
    const t = new Date(timestampIso).toLocaleTimeString("en-US", { hour12: false });
    const labels = latencyChart.data.labels;
    const data = latencyChart.data.datasets[0].data;
    labels.push(t);
    data.push(latencyMs);
    if (labels.length > maxPoints) {
      labels.shift();
      data.shift();
    }
    // moving average (5)
    if (Array.isArray(latencyChart.data.datasets[1].data)){
      const src = latencyChart.data.datasets[0].data;
      const ma = [];
      const window = 5;
      for (let i = 0; i < src.length; i++){
        const start = Math.max(0, i - window + 1);
        const slice = src.slice(start, i + 1);
        const mean = slice.reduce((a, b) => a + b, 0) / slice.length;
        ma.push(Number.isFinite(mean) ? Number(mean.toFixed(1)) : null);
      }
      latencyChart.data.datasets[1].data = ma;
      latencyChart.data.datasets[1].hidden = !userPrefs.enableMA;
    }
    latencyChart.update();
  }

  // Live Charts poller (fallback when SSE metrics are not wiring the specific live API).
  // Polls /api/live/<metric> every 5s, logs status, and updates the primary chart instance.
  // Expects payload: { timestamps: [...], values: [...] }
  (function setupLiveChartsPolling() {
    const POLL_MS = 5000;
    let timer = null;
    async function loadChart() {
      try {
        const selector = document.getElementById('viewSelector');
        const currentMetric = selector ? selector.value : 'latency';
        const endpoint = `/api/live/${currentMetric}`;
        console.log('[LiveCharts] Poll tick →', currentMetric, 'at', new Date().toISOString());

        let data;
        if (USE_DUMMY_DATA) {
          const now = Date.now();
          data = {
            timestamps: [now - 2000, now - 1000, now],
            values: [
              250 + Math.random() * 100,
              300 + Math.random() * 120,
              200 + Math.random() * 180
            ].map(v => Math.round(v))
          };
          console.log('[LiveCharts] Using dummy data:', data);
        } else {
          const res = await fetch(endpoint, { headers: { 'Accept': 'application/json' } });
          console.log('[LiveCharts] Request', endpoint, 'status=', res.status);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          data = await res.json();
          console.log('[LiveCharts] Data returned:', data);
        }

        // Update the primary chart (Chart.js) if present
        const chartRef = window.__chartPrimary && window.__chartPrimary.value;
        const canvas = document.querySelector('#chartPrimary');
        if (!canvas) {
          console.warn('[LiveCharts] #chartPrimary not found; skipping update');
          return;
        }
        const w = canvas.clientWidth, h = canvas.clientHeight;
        console.log('[LiveCharts] Canvas size:', w, 'x', h);
        if (w === 0 || h === 0) {
          // Ensure non-zero rendering area if needed
          canvas.width = canvas.parentElement ? canvas.parentElement.clientWidth : 640;
          canvas.height = canvas.parentElement ? canvas.parentElement.clientHeight : 240;
          console.log('[LiveCharts] Adjusted canvas WH to', canvas.width, 'x', canvas.height);
        }

        if (!chartRef) {
          console.warn('[LiveCharts] Primary chart is not initialized yet');
          return;
        }
        if (!data || !Array.isArray(data.timestamps) || !Array.isArray(data.values)) {
          console.warn('[LiveCharts] Unexpected payload; expected {timestamps, values}', data);
          return;
        }
        // Safety check for chart instance
        if (!chartRef.data || !chartRef.data.datasets) {
          console.warn('[LiveCharts] Chart instance is not properly initialized');
          return;
        }
        // Normalize labels
        const labels = data.timestamps.map(ts =>
          new Date(ts).toLocaleTimeString('en-US', { hour12: false })
        );
        const values = data.values;
        console.log('[LiveCharts] Updating chart with', values.length, 'points');

        // Push points onto the Chart.js instance and keep a rolling window
        const maxPointsPrimary = 60;
        const c = chartRef;
        c.data.labels.push(...labels);
        if (!c.data.datasets[0]) c.data.datasets[0] = { data: [] };
        c.data.datasets[0].data.push(...values);
        while (c.data.labels.length > maxPointsPrimary) c.data.labels.shift();
        while (c.data.datasets[0].data.length > maxPointsPrimary) c.data.datasets[0].data.shift();
        // Optional: update moving average dataset if present
        if (c.data.datasets[1] && Array.isArray(c.data.datasets[1].data)) {
          const src = c.data.datasets[0].data;
          const ma = [];
          const windowN = 5;
          for (let i = 0; i < src.length; i++) {
            const start = Math.max(0, i - windowN + 1);
            const slice = src.slice(start, i + 1);
            const mean = slice.reduce((a, b) => a + b, 0) / slice.length;
            ma.push(Number.isFinite(mean) ? Number(mean.toFixed(1)) : null);
          }
          c.data.datasets[1].data = ma;
        }
        c.update();
        console.log('[LiveCharts] Chart updated');
      } catch (err) {
        console.error('[LiveCharts] Polling error:', err);
      }
    }
    // Start interval
    timer = setInterval(loadChart, POLL_MS);
    // Immediate kick
    loadChart();
  })();

  function updateSuccessRate(value) {
    if (!successRateEl()) return;
    successRateEl().textContent = `${value}%`;
  }

  function updateThroughput(nowMs, timestampIsoForLabel) {
    const ONE_MIN = 60_000;
    const cutoff = nowMs - ONE_MIN;
    // drop older timestamps
    while (eventTimes.length && eventTimes[0] < cutoff) eventTimes.shift();
    throughputEl().textContent = String(eventTimes.length);

    if (throughputChart) {
      const label = new Date(timestampIsoForLabel).toLocaleTimeString("en-US", { hour12: false });
      const labels = throughputChart.data.labels;
      const data = throughputChart.data.datasets[0].data;
      labels.push(label);
      data.push(eventTimes.length);
      if (labels.length > maxPoints) {
        labels.shift();
        data.shift();
      }
      throughputChart.update();
    }
  }

  function appendLogRow(evt) {
    const row = document.createElement("tr");
    const statusBadge = evt.error
      ? `<span class="badge badge-error" title="${String(evt.error)}">Error</span>`
      : `<span class="badge badge-success">OK</span>`;

    row.innerHTML = `
      <td>${new Date(evt.timestamp).toISOString().replace(".000Z", "Z")}</td>
      <td>${evt.bot_name}</td>
      <td>${evt.latency_ms}</td>
      <td>${evt.success_rate}</td>
      <td>${statusBadge}</td>
      <td class="font-mono">${evt.tx_hash}</td>
    `;
    logTableBody().prepend(row);
    // Keep only last 200 rows
    const maxRows = 200;
    while (logTableBody().rows.length > maxRows) {
      logTableBody().deleteRow(logTableBody().rows.length - 1);
    }
  }

  function setSSEStatus(connected) {
    const el = connIndicator();
    if (!el) return;
    if (connected) {
      el.textContent = "Connected";
      el.classList.remove("badge-error");
      el.classList.add("badge-success");
    } else {
      el.textContent = "Disconnected";
      el.classList.remove("badge-success");
      el.classList.add("badge-error");
    }
  }

  // Expose for hx-on or other inline handlers if needed
  window.setSSEStatus = setSSEStatus;
  // Rolling counters for CSS-only ring and sparkline updates
  const ringCounts = { ok: 0, slow: 0, err: 0 };
  const sparklineVals = [];
  const SPARK_MAX = 30;

  function updateChartsFromMetrics(evt){
    try {
      const latency = typeof evt.latency_ms === 'number' ? evt.latency_ms : 0;
      const successPct = typeof evt.success_rate === 'number' ? evt.success_rate : 0;
      const normLatency = Math.max(0, Math.min(1, latency / 500));
      const normSuccess = Math.max(0, Math.min(1, successPct / 100));
      // Throughput proxy from rolling window length
      const normThroughput = Math.max(0, Math.min(1, eventTimes.length / 60));

      // 1) Update quick stat bars in sidebar (first three bars in the aside)
      const asideBars = document.querySelectorAll('aside .css-bar');
      if (asideBars && asideBars.length >= 3) {
        asideBars[0].style.setProperty('--value', normLatency);
        asideBars[1].style.setProperty('--value', normSuccess);
        asideBars[2].style.setProperty('--value', normThroughput);
      }

      // 2) Update status ring by classifying latest latency (rolling distribution)
      if (latency > 0) {
        if (latency < 250) ringCounts.ok += 1;
        else if (latency < 400) ringCounts.slow += 1;
        else ringCounts.err += 1;
        const total = ringCounts.ok + ringCounts.slow + ringCounts.err;
        if (total > 0) {
          const okPct = Math.round((ringCounts.ok / total) * 100);
          const slowPct = Math.round((ringCounts.slow / total) * 100);
          const errPct = Math.max(0, 100 - okPct - slowPct);
          const ring = document.querySelector('.css-status-ring');
          if (ring) {
            ring.style.setProperty('--ok', String(okPct));
            ring.style.setProperty('--slow', String(slowPct));
            ring.style.setProperty('--err', String(errPct));
          }
        }
      }

      // 3) Update sparkline with normalized latency
      if (!Number.isNaN(normLatency)) {
        sparklineVals.push(normLatency);
        while (sparklineVals.length > SPARK_MAX) sparklineVals.shift();
        const spark = document.querySelector('#live-log-sparkline .css-sparkline');
        if (spark) {
          const bars = spark.querySelectorAll('i');
          const pad = Math.max(0, bars.length - sparklineVals.length);
          bars.forEach((bar, idx) => {
            const v = sparklineVals[idx - pad] ?? 0;
            bar.style.setProperty('--v', v);
          });
        }
      }
    } catch (e) {
      // non-fatal
    }
  }

  window.handleMetrics = function(detail) {
    // detail is the event data string per htmx sse extension
    try {
      const evt = typeof detail === "string" ? JSON.parse(detail) : detail;
      const now = Date.now();
      eventTimes.push(now);
      updateThroughput(now, evt.timestamp);
      updateSuccessRate(evt.success_rate);
      updateChart(evt.timestamp, evt.latency_ms);
      appendLogRow(evt);
      if (evt.bot_name && botNameEl()) {
        botNameEl().textContent = String(evt.bot_name);
      }
      
      // Price badge handling
      let priceEl = document.getElementById("price-badge");
      if (!priceEl) {
        const header = document.querySelector("header") || document.body;
        priceEl = document.createElement("div");
        priceEl.id = "price-badge";
        priceEl.style.fontWeight = "600";
        priceEl.style.marginLeft = "12px";
        header.appendChild(priceEl);
      }
      if (evt.price_eth_usd != null) {
        priceEl.textContent = `ETH/USD: ${evt.price_eth_usd.toFixed(2)}`;
      }
      // Update CSS-only charts
      updateChartsFromMetrics(evt);
    } catch (e) {
      console.error("Failed to parse metrics event", e);
    }
  }

  // Load fallback sample data
  async function loadFallbackData() {
    try {
      const response = await fetch('/static/data/sample_metrics.json');
      const data = await response.json();
      console.log('[Fallback] Loaded sample metrics data');
      // Simulate the data stream
      data.forEach((item, index) => {
        setTimeout(() => {
          if (window.handleMetrics) {
            window.handleMetrics(JSON.stringify({
              ...item,
              timestamp: Date.now() - (data.length - index) * 6000
            }));
          }
        }, index * 500);
      });
    } catch (err) {
      console.error('[Fallback] Failed to load sample data:', err);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    // Ensure initial charts are built from the pre-rendered metrics HTML
    const metricsPanel = document.getElementById('metrics-panel');
    if (metricsPanel) {
      try {
        buildOrUpdateChartsFromPartial(metricsPanel);
      } catch (e) {
        console.warn('[LiveCharts] Initial chart init failed', e);
      }
    }
    // Show Sample Mode indicator if present on body dataset
    const body = document.body;
    if (body && body.dataset && body.dataset.sampleMode === "true" && sampleModeBadge()) {
      sampleModeBadge().classList.remove("hidden");
    }
    // load prefs
    try {
      const raw = localStorage.getItem('phoenix:prefs');
      if (raw) userPrefs = { ...userPrefs, ...JSON.parse(raw) };
    } catch {}
    const toggle = document.getElementById('toggleMA');
    const alertI = document.getElementById('alertLatency');
    if (toggle) toggle.checked = !!userPrefs.enableMA;
    if (alertI && userPrefs.alertLatencyMs != null) alertI.value = String(userPrefs.alertLatencyMs);
    
    // Set timeout to load fallback data if no SSE connection after 3 seconds
    setTimeout(() => {
      const statusEl = document.getElementById('conn-status');
      if (statusEl && statusEl.textContent === 'Disconnected') {
        console.log('[Fallback] No SSE connection, loading sample data');
        loadFallbackData();
      }
    }, 3000);
  });

  // HTMX SSE lifecycle events
  document.body.addEventListener("htmx:sseOpen", function() { setSSEStatus(true); });
  document.body.addEventListener("htmx:sseError", function() { setSSEStatus(false); });

  // Sidebar nav and hotkeys
  function setView(view){
    const selector = document.getElementById('viewSelector');
    if (selector){ selector.value = view; selector.dispatchEvent(new Event('change')); }
    const items = document.querySelectorAll('#viewNav .nav-view');
    items.forEach(i => i.classList.toggle('active', i.dataset.view === view));
  }
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('#viewNav .nav-view');
    if (btn){ setView(btn.dataset.view); }
    if (e.target && e.target.id === 'btnResetZoom'){
      if (latencyChart && latencyChart.resetZoom) latencyChart.resetZoom();
      if (throughputChart && throughputChart.resetZoom) throughputChart.resetZoom();
    }
    if (e.target && e.target.id === 'btnSavePrefs'){
      const toggle = document.getElementById('toggleMA');
      const alertI = document.getElementById('alertLatency');
      userPrefs.enableMA = !!(toggle && toggle.checked);
      const v = alertI && alertI.value ? parseInt(alertI.value, 10) : null;
      userPrefs.alertLatencyMs = Number.isFinite(v) ? v : null;
      try { localStorage.setItem('phoenix:prefs', JSON.stringify(userPrefs)); } catch {}
      if (latencyChart){ latencyChart.data.datasets[1].hidden = !userPrefs.enableMA; latencyChart.update('none'); }
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (e.key === '1') setView('latency');
    else if (e.key === '2') setView('throughput');
    else if (e.key === '3') setView('profit');
    else if (e.key === '4') setView('heatmap');
    else if (e.key === '5') setView('graph3d');
    else if (e.key === '6') setView('sensors');
    else if (e.key.toLowerCase() === 'n'){
      const order = ['latency','throughput','profit','heatmap','graph3d','sensors'];
      const selector = document.getElementById('viewSelector');
      const idx = Math.max(0, order.indexOf(selector?.value || 'latency'));
      setView(order[(idx+1)%order.length]);
    } else if (e.key.toLowerCase() === 'p'){
      const order = ['latency','throughput','profit','heatmap','graph3d','sensors'];
      const selector = document.getElementById('viewSelector');
      const idx = Math.max(0, order.indexOf(selector?.value || 'latency'));
      setView(order[(idx-1+order.length)%order.length]);
    }
  });

  // Metrics events from htmx sse extension
  document.body.addEventListener("sse:metrics", function(e) {
    // Alerting check
    try {
      const evt = typeof e.detail === 'string' ? JSON.parse(e.detail) : e.detail;
      if (userPrefs.alertLatencyMs && typeof evt.latency_ms === 'number' && evt.latency_ms >= userPrefs.alertLatencyMs){
        const div = document.createElement('div');
        div.className = 'toast toast-top toast-end';
        div.innerHTML = `<div class="alert alert-warning">High latency ${evt.latency_ms}ms at ${new Date(evt.timestamp).toLocaleTimeString()}</div>`;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 4000);
      }
    } catch {}
    window.handleMetrics(e.detail);
  });

  // Generate chart markers for significant data points
  function generateChartMarkers(labels, data) {
    if (!data || data.length === 0) return {};
    
    const markers = {};
    const threshold = Math.max(...data) * 0.8; // Mark values above 80% of max
    const minThreshold = Math.min(...data) * 1.2; // Mark values below 20% above min
    
      data.forEach((value, index) => {
        if (value >= threshold || value <= minThreshold) {
          const markerId = `marker${index}`;
          markers[markerId] = {
            type: 'point',
            xValue: index,
            yValue: value,
            backgroundColor: 'rgba(0, 191, 255, 0.8)',
            borderColor: 'rgba(0, 191, 255, 1)',
            borderWidth: 2,
            radius: 6,
            pointStyle: 'circle'
          };
        }
      });
    
    return markers;
  }

    // Charts initialization for server-rendered metrics partial (executed after HTMX swap)
  function buildOrUpdateChartsFromPartial(container){
    try {
      const card = container.querySelector('.card[data-latency-labels]');
      if (!card) return;
      
      // Check if 3D graph view is selected
      const viewSelector = document.getElementById('viewSelector');
      const currentView = viewSelector ? viewSelector.value : 'latency';
      
      if (currentView === 'graph3d') {
        // Hide chart canvas, show 3D graph canvas
        const chartPrimary = container.querySelector('#chartPrimary');
        const chartSecondary = container.querySelector('#chartSecondary');
        const graph3dCanvas = container.querySelector('#graph3dCanvas');
        const financial3dCanvas = container.querySelector('#financial3dCanvas');
        const pointcloudContainer = container.querySelector('#pointcloudContainer');
        const toolbar = container.querySelector('#chartToolbar');
        
        if (chartPrimary) chartPrimary.style.display = 'none';
        if (chartSecondary) chartSecondary.style.display = 'none';
        if (pointcloudContainer) pointcloudContainer.style.display = 'none';
        if (financial3dCanvas) financial3dCanvas.style.display = 'none';
        if (toolbar) toolbar.style.display = 'none';
        if (graph3dCanvas) {
          graph3dCanvas.style.display = 'block';
          window.init3DGraph(container);
          setTimeout(() => window.start3DAnimation(), 100);
        }
        return;
      } else if (currentView === 'financial3d') {
        // Hide chart canvas, show financial 3D chart
        const chartPrimary = container.querySelector('#chartPrimary');
        const chartSecondary = container.querySelector('#chartSecondary');
        const graph3dCanvas = container.querySelector('#graph3dCanvas');
        const financial3dCanvas = container.querySelector('#financial3dCanvas');
        const pointcloudContainer = container.querySelector('#pointcloudContainer');
        const toolbar = container.querySelector('#chartToolbar');
        
        if (chartPrimary) chartPrimary.style.display = 'none';
        if (chartSecondary) chartSecondary.style.display = 'none';
        if (graph3dCanvas) graph3dCanvas.style.display = 'none';
        if (pointcloudContainer) pointcloudContainer.style.display = 'none';
        if (toolbar) toolbar.style.display = 'none';
        if (financial3dCanvas) {
          financial3dCanvas.style.display = 'block';
          financial3dCanvas.width = financial3dCanvas.clientWidth;
          financial3dCanvas.height = financial3dCanvas.clientHeight;
          if (window.initFinancial3D) {
            window.initFinancial3D(container);
            // Fetch and update data
            if (window.fetchFinancial3DData) {
              window.fetchFinancial3DData('/api/charts/data');
              // Auto-refresh every 5 seconds
              setInterval(() => {
                if (window.fetchFinancial3DData) {
                  window.fetchFinancial3DData('/api/charts/data');
                }
              }, 5000);
            }
          }
        }
        return;
      } else if (currentView === 'pointcloud') {
        // Hide chart canvas, show point cloud
        const chartPrimary = container.querySelector('#chartPrimary');
        const chartSecondary = container.querySelector('#chartSecondary');
        const graph3dCanvas = container.querySelector('#graph3dCanvas');
        const pointcloudContainer = container.querySelector('#pointcloudContainer');
        const toolbar = container.querySelector('#chartToolbar');
        
        if (chartPrimary) chartPrimary.style.display = 'none';
        if (chartSecondary) chartSecondary.style.display = 'none';
        if (graph3dCanvas) graph3dCanvas.style.display = 'none';
        if (toolbar) toolbar.style.display = 'none';
        if (pointcloudContainer) {
          pointcloudContainer.style.display = 'block';
          // Clean up any existing point cloud
          if (window.cleanupPointCloud) {
            window.cleanupPointCloud();
          }
          // Initialize point cloud
          setTimeout(() => {
            if (window.initPointCloud) {
              window.initPointCloud(pointcloudContainer);
            }
          }, 100);
        }
        return;
      } else {
        // Show normal charts
        const chartPrimary = container.querySelector('#chartPrimary');
        const chartSecondary = container.querySelector('#chartSecondary');
        const graph3dCanvas = container.querySelector('#graph3dCanvas');
        const financial3dCanvas = container.querySelector('#financial3dCanvas');
        const pointcloudContainer = container.querySelector('#pointcloudContainer');
        const toolbar = container.querySelector('#chartToolbar');
        
        if (chartPrimary) chartPrimary.style.display = 'block';
        if (chartSecondary) chartSecondary.style.display = 'block';
        if (toolbar) toolbar.style.display = 'flex';
        if (graph3dCanvas) graph3dCanvas.style.display = 'none';
        if (financial3dCanvas) financial3dCanvas.style.display = 'none';
        if (pointcloudContainer) {
          pointcloudContainer.style.display = 'none';
          if (window.cleanupPointCloud) {
            window.cleanupPointCloud();
          }
        }
        if (window.cleanupFinancial3D) {
          window.cleanupFinancial3D();
        }
      }
      
      const latencyLabels = JSON.parse(card.dataset.latencyLabels || '[]');
      const latencyValues = JSON.parse(card.dataset.latencyValues || '[]');
      const tpLabels = JSON.parse(card.dataset.throughputLabels || '[]');
      const tpValues = JSON.parse(card.dataset.throughputValues || '[]');
      const pfLabels = JSON.parse(card.dataset.profitLabels || '[]');
      const pfValues = JSON.parse(card.dataset.profitValues || '[]');
      const heatCells = JSON.parse(card.dataset.heatCells || '[]');
      const heatCols = parseInt(card.dataset.heatCols || '12', 10);
      const sensorLabels = JSON.parse(card.dataset.sensorLabels || '[]');
      const sensorTempValues = JSON.parse(card.dataset.sensorTempValues || '[]');
      const sensorHumValues = JSON.parse(card.dataset.sensorHumidityValues || '[]');

      const colors = {
        primary: 'rgba(0, 191, 255, 1)',
        secondary: 'rgba(0, 255, 136, 1)',
        accent: 'rgba(240, 240, 240, 1)'
      };

      const ctx1 = container.querySelector('#chartPrimary');
      const ctx2 = container.querySelector('#chartSecondary');
      if (!ctx1 || !ctx2) return;

      function ensureLineChart(instanceRef, ctx, labels, data, label, color){
        // Generate markers based on data peaks/valleys
        const annotations = generateChartMarkers(labels, data);
        
        // Convert color to RGBA with alpha for fill
        const rgbaColor = color.replace('1)', '0.15)');
        
        if (!instanceRef.value){
          instanceRef.value = new Chart(ctx, {
            type: 'line',
            data: { 
              labels, 
              datasets: [{ 
                label, 
                data, 
                borderColor: color, 
                backgroundColor: rgbaColor, 
                borderWidth: 3, 
                tension: 0.25, 
                pointRadius: 4, 
                pointHoverRadius: 8,
                fill: true
              }] 
            },
            options: { 
              responsive: true, 
              maintainAspectRatio: false, 
              animation: false, 
              plugins: { 
                legend: { display: false },
                annotation: { annotations }
              }, 
              scales: { 
                y: { 
                  beginAtZero: true,
                  grid: {
                    color: 'rgba(128, 128, 128, 0.2)'
                  },
                  ticks: {
                    color: 'rgba(240, 240, 240, 0.8)'
                  }
                },
                x: {
                  grid: {
                    color: 'rgba(128, 128, 128, 0.2)'
                  },
                  ticks: {
                    color: 'rgba(240, 240, 240, 0.8)'
                  }
                }
              }
            }
          });
        } else {
          const c = instanceRef.value;
          c.data.labels = labels; 
          c.data.datasets[0].data = data; 
          // Update annotations with new markers
          if (c.options.plugins && c.options.plugins.annotation) {
            c.options.plugins.annotation.annotations = annotations;
          }
          c.update('none');
        }
      }

      function ensureHeatmap(instanceRef, ctx, cells, cols){
        const data = cells.map(c => ({x: c.x, y: c.y, v: c.v}));
        const maxV = data.reduce((m, c) => Math.max(m, c.v), 1);
        if (!instanceRef.value){
          instanceRef.value = new Chart(ctx, {
            type: 'matrix',
            data: { datasets: [{
              label: 'Latency Heatmap',
              data,
              backgroundColor(ctx){ const v = ctx.raw.v||0; const alpha = v/maxV; return `hsla(191 100% 46% / ${alpha})`; },
              borderWidth: 1,
              width: ({chart}) => (chart.chartArea.right - chart.chartArea.left)/cols - 2,
              height: ({chart}) => (chart.chartArea.bottom - chart.chartArea.top)/4 - 2,
              xAxisID: 'x', yAxisID: 'y'
            }] },
            options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display:false, offset:true }, y: { display:false, offset:true, reverse:true } } }
          });
        } else {
          const c = instanceRef.value; c.data.datasets[0].data = data; c.update('none');
        }
      }

      window.__chartPrimary = window.__chartPrimary || { value: null };
      window.__chartSecondary = window.__chartSecondary || { value: null };

      // Initialize defaults when partial first arrives
      const selector = container.querySelector('#viewSelector');
      const current = selector ? selector.value : 'latency';
      if (current === 'latency'){
        ensureLineChart(window.__chartPrimary, ctx1, latencyLabels, latencyValues, 'Latency (ms)', colors.primary);
        ensureLineChart(window.__chartSecondary, ctx2, tpLabels, tpValues, 'Throughput (/min)', colors.secondary);
      } else if (current === 'throughput'){
        ensureLineChart(window.__chartPrimary, ctx1, tpLabels, tpValues, 'Throughput (/min)', colors.primary);
        ensureLineChart(window.__chartSecondary, ctx2, latencyLabels, latencyValues, 'Latency (ms)', colors.secondary);
      } else if (current === 'profit'){
        ensureLineChart(window.__chartPrimary, ctx1, pfLabels, pfValues, 'Cumulative Profit', colors.primary);
        ensureLineChart(window.__chartSecondary, ctx2, tpLabels, tpValues, 'Throughput (/min)', colors.secondary);
      } else if (current === 'heatmap'){
        ensureHeatmap(window.__chartPrimary, ctx1, heatCells, heatCols);
        ensureLineChart(window.__chartSecondary, ctx2, latencyLabels, latencyValues, 'Latency (ms)', colors.primary);
      } else if (current === 'graph3d'){
        // 3D graph is handled separately above
        return;
      } else if (current === 'financial3d'){
        // Financial 3D chart is handled separately above
        return;
      } else if (current === 'sensors'){
        ensureLineChart(window.__chartPrimary, ctx1, sensorLabels, sensorTempValues, 'Temperature (°C)', colors.primary);
        ensureLineChart(window.__chartSecondary, ctx2, sensorLabels, sensorHumValues, 'Humidity (%)', colors.secondary);
      }
    } catch (err) {
      console.error('Failed to init charts from partial', err);
    }
  }

  document.body.addEventListener('htmx:afterSwap', function(e){
    if (e && e.target && e.target.id === 'metrics-panel'){
      buildOrUpdateChartsFromPartial(e.target);
      // Re-bind toolbar states on new partial
      const toggle = document.getElementById('toggleMA');
      const alertI = document.getElementById('alertLatency');
      if (toggle) toggle.checked = !!userPrefs.enableMA;
      if (alertI && userPrefs.alertLatencyMs != null) alertI.value = String(userPrefs.alertLatencyMs);
      
      // Add view selector handler
      const selector = e.target.querySelector('#viewSelector');
      if (selector) {
        selector.addEventListener('change', function() {
          buildOrUpdateChartsFromPartial(e.target);
        });
      }
      
      // Initialize Bot Health Table if present
      const botHealthContainer = e.target.querySelector('[data-bot-health-table]');
      if (botHealthContainer && typeof BotHealthTable !== 'undefined') {
        // Clean up existing instance if any
        if (botHealthContainer._botHealthTable) {
          botHealthContainer._botHealthTable.destroy();
        }
        
        const containerId = botHealthContainer.id || `bot-health-table-${Date.now()}`;
        if (!botHealthContainer.id) {
          botHealthContainer.id = containerId;
        }
        
        const refreshInterval = botHealthContainer.dataset.refreshInterval 
          ? parseInt(botHealthContainer.dataset.refreshInterval, 10) 
          : 5000;
        
        const apiEndpoint = botHealthContainer.dataset.apiEndpoint || '/api/bots/status';
        
        const table = new BotHealthTable(containerId, {
          refreshInterval,
          apiEndpoint
        });
        table.init();
        botHealthContainer._botHealthTable = table;
      }
    }
  });

  // Keyboard shortcut to reset zoom
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'z' || e.key === 'Z') && !e.metaKey && !e.ctrlKey && !e.altKey){
      if (latencyChart && latencyChart.resetZoom) latencyChart.resetZoom();
      if (throughputChart && throughputChart.resetZoom) throughputChart.resetZoom();
    }
  });

  // TV Channel Controls
  let currentChannel = 1;
  let currentView = 'latency';

  function switchChannel(channelNumber, view) {
    // Remove active class from all channels
    document.querySelectorAll('.channel-dial').forEach(dial => {
      dial.classList.remove('active');
    });
    
    // Add active class to selected channel
    const selectedDial = document.getElementById(`channel-${channelNumber}`);
    if (selectedDial) {
      selectedDial.classList.add('active');
    }
    
    // Update channel indicator
    const indicator = document.getElementById('current-channel');
    if (indicator) {
      indicator.textContent = channelNumber;
    }
    
    // Switch view
    currentChannel = channelNumber;
    currentView = view;
    setView(view);
    
    // Brief static effect when switching
    const staticOverlay = document.querySelector('.tv-static');
    if (staticOverlay) {
      staticOverlay.style.opacity = '0.4';
      setTimeout(() => {
        staticOverlay.style.opacity = '0.2';
      }, 150);
    }
  }

  // TV Channel event listeners
  document.addEventListener('click', (e) => {
    const dial = e.target.closest('.channel-dial');
    if (!dial) return;

    const channelNumber = parseInt(dial.dataset.channel);
    const view = dial.dataset.view;
    
    switchChannel(channelNumber, view);
  });
})();


