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
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: false } },
          y: { beginAtZero: true },
        },
        plugins: { legend: { display: false } },
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
        plugins: { legend: { display: false } },
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
  });

  // HTMX SSE lifecycle events
  document.body.addEventListener("htmx:sseOpen", function() { setSSEStatus(true); });
  document.body.addEventListener("htmx:sseError", function() { setSSEStatus(false); });

  // Metrics events from htmx sse extension
  document.body.addEventListener("sse:metrics", function(e) {
    window.handleMetrics(e.detail);
  });
})();


