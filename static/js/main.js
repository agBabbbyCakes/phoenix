(() => {
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
            borderColor: "#60a5fa",
            backgroundColor: "rgba(96,165,250,0.2)",
            borderWidth: 2,
            tension: 0.25,
            pointRadius: 2,
          },
          {
            label: "MA(5)",
            data: [],
            borderColor: "#f59e0b",
            backgroundColor: "rgba(245,158,11,0.15)",
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
            borderColor: "#34d399",
            backgroundColor: "rgba(52,211,153,0.2)",
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
    } catch (e) {
      console.error("Failed to parse metrics event", e);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    initCharts();
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
    else if (e.key === '5') setView('sensors');
    else if (e.key.toLowerCase() === 'n'){
      const order = ['latency','throughput','profit','heatmap','sensors'];
      const selector = document.getElementById('viewSelector');
      const idx = Math.max(0, order.indexOf(selector?.value || 'latency'));
      setView(order[(idx+1)%order.length]);
    } else if (e.key.toLowerCase() === 'p'){
      const order = ['latency','throughput','profit','heatmap','sensors'];
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

  // Charts initialization for server-rendered metrics partial (executed after HTMX swap)
  function buildOrUpdateChartsFromPartial(container){
    try {
      const card = container.querySelector('.card[data-latency-labels]');
      if (!card) return;
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
        cyan: 'hsl(191 100% 46%)',
        magenta: 'hsl(320 90% 70%)',
        yellow: 'hsl(45 100% 60%)'
      };

      const ctx1 = container.querySelector('#chartPrimary');
      const ctx2 = container.querySelector('#chartSecondary');
      if (!ctx1 || !ctx2) return;

      function ensureLineChart(instanceRef, ctx, labels, data, label, color){
        if (!instanceRef.value){
          instanceRef.value = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets: [{ label, data, borderColor: color, backgroundColor: color.replace('hsl', 'hsla').replace(')', '/.2)'), borderWidth: 2, tension: 0.25, pointRadius: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, animation: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
          });
        } else {
          const c = instanceRef.value;
          c.data.labels = labels; c.data.datasets[0].data = data; c.update('none');
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
        ensureLineChart(window.__chartPrimary, ctx1, latencyLabels, latencyValues, 'Latency (ms)', colors.cyan);
        ensureLineChart(window.__chartSecondary, ctx2, tpLabels, tpValues, 'Throughput (/min)', colors.magenta);
      } else if (current === 'throughput'){
        ensureLineChart(window.__chartPrimary, ctx1, tpLabels, tpValues, 'Throughput (/min)', colors.magenta);
        ensureLineChart(window.__chartSecondary, ctx2, latencyLabels, latencyValues, 'Latency (ms)', colors.cyan);
      } else if (current === 'profit'){
        ensureLineChart(window.__chartPrimary, ctx1, pfLabels, pfValues, 'Cumulative Profit', colors.yellow);
        ensureLineChart(window.__chartSecondary, ctx2, tpLabels, tpValues, 'Throughput (/min)', colors.magenta);
      } else if (current === 'heatmap'){
        ensureHeatmap(window.__chartPrimary, ctx1, heatCells, heatCols);
        ensureLineChart(window.__chartSecondary, ctx2, latencyLabels, latencyValues, 'Latency (ms)', colors.cyan);
      } else if (current === 'sensors'){
        ensureLineChart(window.__chartPrimary, ctx1, sensorLabels, sensorTempValues, 'Temperature (°C)', colors.cyan);
        ensureLineChart(window.__chartSecondary, ctx2, sensorLabels, sensorHumValues, 'Humidity (%)', colors.magenta);
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
    }
  });

  // Keyboard shortcut to reset zoom
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'z' || e.key === 'Z') && !e.metaKey && !e.ctrlKey && !e.altKey){
      if (latencyChart && latencyChart.resetZoom) latencyChart.resetZoom();
      if (throughputChart && throughputChart.resetZoom) throughputChart.resetZoom();
    }
  });

  // 3D Dial Controls
  let currentViewpoint = 1;
  let currentChart = 'latency';
  let currentZoom = 1;
  let currentGlow = 'cyan';

  function update3DView() {
    const panel = document.getElementById('metrics-panel');
    if (panel) {
      panel.className = `chart-3d view-${currentViewpoint}`;
      panel.style.transform = `scale(${currentZoom})`;
    }
    
    // Update glow effects
    document.querySelectorAll('.glow-cyan, .glow-magenta, .glow-yellow').forEach(el => {
      el.classList.remove('glow-cyan', 'glow-magenta', 'glow-yellow');
      el.classList.add(`glow-${currentGlow}`);
    });
  }

  function rotateDial(dial, steps) {
    const knob = dial.querySelector('.dial-knob');
    const currentRotation = parseInt(dial.dataset.rotation || '0');
    const newRotation = (currentRotation + steps * 45) % 360;
    dial.dataset.rotation = newRotation;
    knob.style.transform = `translate(-50%, -50%) rotate(${newRotation}deg)`;
  }

  // Dial event listeners
  document.addEventListener('click', (e) => {
    const dial = e.target.closest('.dial');
    if (!dial) return;

    if (dial.id === 'viewpoint-dial') {
      currentViewpoint = currentViewpoint >= 5 ? 1 : currentViewpoint + 1;
      dial.dataset.viewpoint = currentViewpoint;
      dial.querySelector('.dial-value').textContent = currentViewpoint;
      rotateDial(dial, 1);
      update3DView();
    }
    else if (dial.id === 'chart-dial') {
      const charts = ['latency', 'throughput', 'profit', 'heatmap', 'sensors'];
      const currentIndex = charts.indexOf(currentChart);
      const nextIndex = (currentIndex + 1) % charts.length;
      currentChart = charts[nextIndex];
      dial.dataset.chart = currentChart;
      dial.querySelector('.dial-value').textContent = currentChart.charAt(0).toUpperCase();
      rotateDial(dial, 1);
      setView(currentChart);
    }
    else if (dial.id === 'zoom-dial') {
      currentZoom = currentZoom >= 2 ? 0.5 : currentZoom + 0.25;
      dial.dataset.zoom = currentZoom;
      dial.querySelector('.dial-value').textContent = currentZoom + 'x';
      rotateDial(dial, 1);
      update3DView();
    }
    else if (dial.id === 'glow-dial') {
      const glows = ['cyan', 'magenta', 'yellow'];
      const currentIndex = glows.indexOf(currentGlow);
      const nextIndex = (currentIndex + 1) % glows.length;
      currentGlow = glows[nextIndex];
      dial.dataset.glow = currentGlow;
      dial.querySelector('.dial-value').textContent = currentGlow.charAt(0).toUpperCase();
      rotateDial(dial, 1);
      update3DView();
    }
  });
})();


