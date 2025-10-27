# Phoenix Ethereum Bot Monitoring Dashboard

## Running the Application

### Option 1: Simple Launch
```bash
python app.py
```
The app will start on `http://127.0.0.1:8000`

### Option 2: Build Standalone macOS App
```bash
./build_macos_app.sh
```

This will create `dist/Phoenix.app` which you can double-click to run.

**Note:** The first time you open the app, macOS may show a security warning. Right-click the app and select "Open" to bypass this.

## Features
- Real-time Ethereum bot monitoring with SSE updates
- Mock data mode (default) or real ETH blockchain data
- Interactive dashboard with charts and metrics

## Environment Variables (Optional)

To use real Ethereum blockchain data instead of mock data:

```bash
# Create a .env file
cat > .env << 'ENVEOF'
ETH_HTTP_URL=https://your-ethereum-http-url
# OR use ETH_WSS_URL for websocket (will convert to HTTP)
ETH_WSS_URL=wss://your-ethereum-websocket-url
CHAINLINK_ETHUSD=your-chainlink-eth-usd-address
ENVEOF
```

Without these variables, the app will use mock data automatically.
