// LiveChart: manages a single Charts.css cell by updating its --size,
// and computes simple rolling metrics for the right-hand panel.
// This avoids DOM churn (no new <tr> spam) and ensures stable rendering.

export class LiveChart {
  constructor(options = {}) {
    const {
      maxMs = 500,
      thresholdMs = 350,
      barEl = document.getElementById('bar'),
      barLabelEl = document.getElementById('bar-label'),
      statCurrentEl = document.getElementById('stat-current'),
      statMaEl = document.getElementById('stat-ma'),
      thresholdEl = document.getElementById('threshold'),
      thresholdLabelEl = document.getElementById('stat-threshold'),
      healthDotEl = document.getElementById('health-indicator'),
      healthStateEl = document.getElementById('health-state'),
      windowSeconds = 5,
    } = options;

    this.maxMs = maxMs;
    this.thresholdMs = thresholdMs;
    this.barEl = barEl;
    this.barLabelEl = barLabelEl;
    this.statCurrentEl = statCurrentEl;
    this.statMaEl = statMaEl;
    this.thresholdEl = thresholdEl;
    this.thresholdLabelEl = thresholdLabelEl;
    this.healthDotEl = healthDotEl;
    this.healthStateEl = healthStateEl;
    this.windowSeconds = windowSeconds;
    this.samples = []; // { t, v }

    if (this.thresholdEl) {
      this.thresholdEl.value = String(this.thresholdMs);
      this.thresholdEl.addEventListener('input', () => {
        this.setThreshold(parseInt(this.thresholdEl.value, 10));
      });
    }
    if (this.thresholdLabelEl) {
      this.thresholdLabelEl.textContent = `${this.thresholdMs} ms`;
    }
  }

  setThreshold(ms) {
    this.thresholdMs = ms;
    if (this.thresholdLabelEl) {
      this.thresholdLabelEl.textContent = `${ms} ms`;
    }
    // Health may change at same current value
    if (this.lastValue != null) {
      this.#updateHealth(this.lastValue);
    }
  }

  setValue(ms) {
    const clamped = Math.max(0, Math.min(this.maxMs, ms));
    const size = clamped / this.maxMs;
    // Update Charts.css bar (single cell)
    if (this.barEl) {
      this.barEl.style.setProperty('--size', size.toFixed(3));
    }
    if (this.barLabelEl) {
      this.barLabelEl.textContent = `${Math.round(clamped)} ms`;
    }
    if (this.statCurrentEl) {
      this.statCurrentEl.textContent = `${Math.round(clamped)} ms`;
    }
    this.#pushSample(clamped);
    const ma = this.#movingAverageMs();
    if (this.statMaEl) {
      this.statMaEl.textContent = isNaN(ma) ? '—' : `${Math.round(ma)} ms`;
    }
    this.#updateHealth(clamped);
    this.lastValue = clamped;
  }

  #pushSample(v) {
    const now = performance.now();
    this.samples.push({ t: now, v });
    const cutoff = now - this.windowSeconds * 1000;
    // Drop old samples outside window
    while (this.samples.length && this.samples[0].t < cutoff) {
      this.samples.shift();
    }
  }

  #movingAverageMs() {
    if (!this.samples.length) return NaN;
    let sum = 0;
    for (const s of this.samples) sum += s.v;
    return sum / this.samples.length;
  }

  #updateHealth(ms) {
    if (!this.healthDotEl || !this.healthStateEl) return;
    // Health tiers:
    // - ok: <= threshold
    // - warn: within +10% over threshold
    // - crit: > threshold + 10%
    const warnBand = this.thresholdMs * 1.1;
    const classes = this.healthDotEl.classList;
    classes.remove('ok', 'warn', 'crit');
    let state = '—';
    if (ms <= this.thresholdMs) {
      classes.add('ok');
      state = 'OK';
    } else if (ms <= warnBand) {
      classes.add('warn');
      state = 'Warning';
    } else {
      classes.add('crit');
      state = 'Critical';
    }
    this.healthStateEl.textContent = state;
  }
}

export default LiveChart;


