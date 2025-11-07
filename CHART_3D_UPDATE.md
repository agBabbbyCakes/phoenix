# 3D Financial Chart & Installer Build System

## Overview

This update adds a 3D financial-style chart visualization (inspired by Fidelity positions charts) with dark, sassy colors, and a complete build system for creating installers on Mac, Windows, and Linux.

## New Features

### 1. 3D Financial Chart (`financial3d.js`)

A new 3D visualization component that:
- **Reads JSON data** from `/api/charts/data` endpoint
- **Displays metrics in 3D** with bars/candles showing:
  - Latency (height of bars)
  - Profit/Loss (color coding: green for profit, red for loss)
  - Status indicators (warning, error, ok)
- **Dark, sassy color palette**:
  - Background: Very dark blue-black (`#0a0a0f`)
  - Profit: Bright green (`#00ff88`)
  - Loss: Bright red (`#ff3b5c`)
  - Neutral: Blue (`#4a90e2`)
  - Warning: Orange (`#ffa500`)
  - Accents: Purple and cyan glows
- **Interactive controls**:
  - Mouse drag to rotate
  - Mouse wheel to zoom
  - Auto-refreshes every 5 seconds
  - Smooth animations

### 2. New API Endpoint

**`GET /api/charts/data`**
- Returns JSON data for 3D chart visualization
- Includes last 100 events with all metrics
- Format:
  ```json
  {
    "events": [...],
    "count": 100,
    "kpis": {...}
  }
  ```

### 3. Build System

Three build scripts for creating installers:

#### macOS (`build_macos.sh`)
- Creates `.app` bundle
- Optional DMG creation instructions included
- Uses Briefcase for packaging

#### Windows (`build_windows.sh`)
- Creates `.msi` installer
- Uses Briefcase for packaging

#### Linux (`build_linux.sh`)
- Creates `.AppImage` (portable)
- Uses Briefcase for packaging

## Usage

### Viewing the 3D Financial Chart

1. Start the app (or run in dev mode)
2. Navigate to the dashboard
3. Select "3D Financial Chart" from the view selector dropdown
4. The chart will automatically fetch and display data

### Building Installers

#### macOS
```bash
./build_macos.sh
```

#### Windows
```bash
./build_windows.sh
```

#### Linux
```bash
./build_linux.sh
```

See `BUILD_INSTALLERS.md` for detailed instructions.

## Technical Details

### Chart Data Flow

1. **Data Source**: Events stored in `DataStore`
2. **API Endpoint**: `/api/charts/data` serves JSON
3. **Chart Component**: `financial3d.js` fetches and renders
4. **Auto-refresh**: Updates every 5 seconds

### Color Scheme

The chart uses a Fidelity-inspired dark theme:
- **Background**: `#0a0a0f` (very dark blue-black)
- **Grid**: `#1a1a2e` (dark blue-gray)
- **Profit bars**: `#00ff88` (bright green)
- **Loss bars**: `#ff3b5c` (bright red)
- **Neutral bars**: `#4a90e2` (blue)
- **Warning bars**: `#ffa500` (orange)
- **Glow effects**: `#00bfff` (cyan)

### 3D Visualization

- Uses Three.js for 3D rendering
- Bars represent metrics (latency, profit, etc.)
- Connecting lines show trends
- Glow effects highlight important data points
- Smooth camera controls (OrbitControls or fallback)

## Files Added/Modified

### New Files
- `static/js/financial3d.js` - 3D financial chart component
- `build_macos.sh` - macOS build script
- `build_windows.sh` - Windows build script
- `build_linux.sh` - Linux build script
- `BUILD_INSTALLERS.md` - Build documentation
- `CHART_3D_UPDATE.md` - This file

### Modified Files
- `app/main.py` - Added `/api/charts/data` endpoint
- `templates/partials/metrics.html` - Added financial3d canvas and option
- `templates/index.html` - Added financial3d.js script
- `templates/base.html` - Added financial3d.js and OrbitControls
- `static/js/main.js` - Integrated financial3d chart view

## Dependencies

- **Three.js** (already included)
- **Briefcase** (for building installers): `pip install briefcase`

## Notes

- The chart automatically handles missing OrbitControls (falls back to simple mouse controls)
- Data is fetched from the existing `DataStore` - no new data sources needed
- The chart works with any JSON data format that includes `latency_ms`, `profit`, or `status` fields
- All colors are dark-themed and "sassy" as requested

## Future Enhancements

Potential improvements:
- Add candlestick-style visualization for profit/loss
- Add time-based animation
- Add tooltips showing detailed metrics
- Add export functionality
- Add more chart types (surface plots, etc.)

