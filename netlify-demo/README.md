# Netlify Demo Widget

This is a standalone HTML widget that connects to your BotScope server and displays live metrics.

## Setup

1. **Deploy your BotScope server** (to Render.com, Railway, etc.) with `FORCE_SAMPLE=1`
2. **Update the server URL** in `index.html`:
   ```javascript
   const SERVER_URL = 'https://your-app.onrender.com'; // Change this!
   ```
3. **Deploy to Netlify**:
   - Drag the `netlify-demo` folder to netlify.com
   - Or connect to GitHub and set build folder to `netlify-demo`

## Features

- Live SSE connection to your server
- Real-time charts (latency, throughput)
- KPI cards (avg latency, success rate, throughput)
- Recent events table
- Zoom/pan controls (press Z to reset)
- Responsive design

## Local Testing

Open `index.html` in a browser after updating the `SERVER_URL`.

## Sharing

Once deployed to Netlify, you'll get a URL like:
`https://amazing-demo-123.netlify.app`

Share this with your boss for instant access to the live demo!
