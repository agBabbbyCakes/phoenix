# Live Charts (QuikUI Streaming HTML Demo)

This example shows a clean, real‑time chart using a single element updated via CSS custom property, and a right‑hand stats panel with a moving average and health indicator.

Key goals achieved:

- Single row/element for the chart; no `<tr>` or `<li>` spamming.
- Uses streaming HTML updates when available.
- Smooth, stable rendering without flicker (we only mutate `--size`).
- Right panel shows current value, 5s moving average, threshold and health color.

## Files

- `index.html` — Two‑panel layout (chart + stats)
- `styles.css` — Minimal styling and layout
- `chart.js` — Chart + stats logic (updates a single cell’s `--size`)
- `stream.js` — Connects to streaming endpoint, parses HTML chunks; mock fallback

## Running

This repository includes a FastAPI app that already exposes a streaming HTML endpoint at:

- `GET /charts/mini` — Streams small chart `<li>` elements with `--size` values

The example connects to that endpoint and reads streamed chunks, extracting `--size` without inserting the incoming elements into the DOM. The single chart cell is updated based on the parsed values.

Steps:

1. Start the app (any of the standard commands you use for this repo).
2. Visit the example in your browser by opening this file directly or hosting the `/examples` folder statically.
   - If served under the same origin as the app, the example will connect to `/charts/mini` automatically.
3. If the stream is unreachable, click “Use mock data” or it will automatically fall back to a random generator.

## Behavior

- The left panel is a Charts.css column chart with one row. We update the `--size` of that cell dynamically.
- The right panel shows:
  - Current data point (e.g., latency in ms)
  - 5s moving average (rolling window)
  - Color health indicator:
    - Green: `<= threshold`
    - Yellow: `<= threshold + 10%`
    - Red: `> threshold + 10%`
  - An adjustable threshold slider (default `350 ms`)

## Notes

- If you prefer not to rely on Charts.css, you can swap the left panel to a minimal `<canvas>` renderer. The logic in `chart.js` provides the normalized value; you would just draw a single bar to canvas instead of using the Tables/CSS approach.
- For production, consider normalizing and scaling to your metric domain (we default to `0–500 ms`).


