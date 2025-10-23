# Netlify Demo Widget

This is a standalone HTML widget that connects to your BotScope server and displays live metrics with **Ethereum realtime overlay**.

## Setup

1. **Deploy your BotScope server** (to Render.com, Railway, etc.) with Ethereum overlay enabled
2. **Update the server URL** in `index.html`:
   ```javascript
   const SERVER_URL = 'https://your-app.onrender.com'; // Change this!
   ```
3. **Deploy to Netlify**:
   - Drag the `netlify-demo` folder to netlify.com
   - Or connect to GitHub and set build folder to `netlify-demo`

## Features

- Live SSE connection to your server
- **Real-time ETH/USD price from Chainlink** (displays in header badge)
- Real-time charts (latency, throughput)
- KPI cards (avg latency, success rate, throughput)
- Recent events table with transaction hashes
- Zoom/pan controls (press Z to reset)
- Responsive 16:9 TV format design
- TV channel controls for different views

## Ethereum Integration

The demo now includes:
- **ETH/USD price badge** that updates in real-time
- **Transaction hash display** in the events table
- **Block-based metrics** from Ethereum mainnet
- **Chainlink price feeds** integration

## Local Testing

1. Start your BotScope server with Ethereum overlay:
   ```bash
   make run-api
   ```

2. Open `index.html` in a browser (the SERVER_URL is set to localhost:8000)

## Production Deployment

For production, update the SERVER_URL in `index.html` to point to your deployed server.

## Sharing

Once deployed to Netlify, you'll get a URL like:
`https://amazing-demo-123.netlify.app`

Share this with your boss for instant access to the live Ethereum monitoring demo!
