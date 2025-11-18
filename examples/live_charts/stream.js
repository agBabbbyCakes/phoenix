import LiveChart from './chart.js';

// Parse streamed HTML chunks from /charts/mini and extract --size values.
// We DO NOT append streamed <li> elements; instead, we read each size and
// drive a single bar via CSS var. This keeps the DOM stable (no flicker).

const chart = new LiveChart({
  maxMs: 500,
  thresholdMs: 350,
});

const toggleBtn = document.getElementById('toggle-mock');
let useMock = false;
let activeAbort = null;
let mockTimer = null;

function startMock() {
  stopAll();
  useMock = true;
  if (toggleBtn) toggleBtn.setAttribute('aria-pressed', 'true');
  // Jittered timer to simulate uneven server pacing
  const tick = () => {
    const v = Math.round(80 + Math.random() * 420); // 80–500 ms
    chart.setValue(v);
    const next = 500 + Math.random() * 1200; // 0.5–1.7s
    mockTimer = setTimeout(tick, next);
  };
  tick();
}

function stopMock() {
  if (mockTimer) {
    clearTimeout(mockTimer);
    mockTimer = null;
  }
}

function stopAll() {
  stopMock();
  if (activeAbort) {
    activeAbort.abort();
    activeAbort = null;
  }
}

async function startStreaming() {
  stopAll();
  useMock = false;
  if (toggleBtn) toggleBtn.setAttribute('aria-pressed', 'false');

  // Prefer QuikUI-style streaming HTML endpoint available in this app:
  // /charts/mini streams <li style="--size: X.XXX;">…</li> lines.
  const url = '/charts/mini';
  const ac = new AbortController();
  activeAbort = ac;

  try {
    const res = await fetch(url, { signal: ac.signal, headers: { Accept: 'text/html' } });
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const regex = /--size:\s*([0-9.]+)/i;
    const MAX_MS = chart.maxMs || 500;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // Split by newlines to try to extract complete <li> lines
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        const m = regex.exec(line);
        if (m) {
          const size = Math.max(0, Math.min(1, parseFloat(m[1])));
          const ms = Math.round(size * MAX_MS);
          chart.setValue(ms);
        }
      }
    }
  } catch (err) {
    // If the streaming endpoint isn't reachable, fall back to mock mode
    startMock();
  } finally {
    if (activeAbort === ac) {
      activeAbort = null;
    }
  }
}

if (toggleBtn) {
  toggleBtn.addEventListener('click', () => {
    if (useMock) {
      startStreaming();
    } else {
      startMock();
    }
  });
}

// Kick off with streaming; if not available, it will gracefully fall back to mock.
startStreaming();


