# Native Desktop Application Features

## Overview

Phoenix Dashboard is now a full-featured native desktop application with professional desktop integration.

## Native Features

### ✅ Native Window
- **Resizable window** - Drag edges to resize
- **Minimize/Maximize** - Standard window controls
- **Window shadow** - Native OS shadow effects
- **Text selection** - Select and copy text from dashboard
- **Native frame** - OS-native window decorations

### ✅ Native Menu Bar (macOS)
- **File Menu:**
  - Refresh (F5)
  - Exit
  
- **View Menu:**
  - Reload (Ctrl+R / Cmd+R)
  - Go Back (Alt+Left)
  - Go Forward (Alt+Right)
  - Developer Tools (F12)

- **Dashboard Menu:**
  - Home
  - Bot Explorer
  - Chart Annotations
  - Logic Builder
  - Downloads
  - Settings

- **Help Menu:**
  - About

### ✅ Keyboard Shortcuts
- **F5** - Refresh page
- **Ctrl+R / Cmd+R** - Reload
- **Alt+Left** - Go back
- **Alt+Right** - Go forward
- **F12** - Developer tools

### ✅ Navigation
- Built-in navigation functions
- History support (back/forward)
- Direct navigation to dashboard sections
- URL management

## Platform-Specific Features

### Windows
- Uses WebView2 (native Windows webview)
- Standard Windows window controls
- Windows-style menus (via pywebview)
- System integration

### macOS
- Uses WKWebView (native macOS webview)
- Native macOS menu bar
- macOS-style window controls
- Full macOS integration

### Linux
- Uses WebKitGTK (native Linux webview)
- GTK window controls
- Linux desktop integration

## Window Configuration

- **Default Size:** 1400x900 pixels
- **Minimum Size:** 800x600 pixels
- **Resizable:** Yes
- **Fullscreen:** No (can be enabled)
- **Always on Top:** No (can be enabled)
- **Frameless:** No (native frame with controls)

## Installation

### Windows Installer

**Using Inno Setup (Recommended):**
```batch
build_windows_installer_innosetup.bat
```

**Features:**
- Professional installation wizard
- Start Menu shortcuts
- Desktop shortcut (optional)
- Uninstaller
- Registry entries
- Admin privileges handling

**Requirements:**
- Inno Setup from https://jrsoftware.org/isinfo.php
- `iscc.exe` in PATH

**Output:**
- `dist/PhoenixDashboard-Setup.exe`
- `downloads/windows/PhoenixDashboard-Setup-x64.exe`

## Future Enhancements

Possible additions:
- ✅ System tray icon with menu
- ✅ Custom toolbar with buttons
- ✅ Window state persistence (remember size/position)
- ✅ Multiple window support
- ✅ Native notifications
- ✅ File associations
- ✅ Drag and drop support
- ✅ Custom window styling

## Technical Details

### Dependencies
- **pywebview** - Native webview wrapper
- **uvicorn** - ASGI server
- **FastAPI** - Web framework

### Architecture
- Server runs on `127.0.0.1:8000` (or next available)
- Webview loads dashboard from local server
- Native window provides desktop integration
- Clean shutdown when window closes

## Building

All platforms use the enhanced launcher:
- `standalone_app_enhanced.py` - Full-featured desktop app
- Native menus, shortcuts, and navigation
- Professional desktop experience

Enjoy your native desktop application! 🚀


