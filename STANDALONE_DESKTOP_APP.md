# Standalone Desktop Application

Phoenix Dashboard now runs as a true standalone desktop application with its own native window!

## Features

✅ **Native Window** - Opens in its own window, not a browser  
✅ **Cross-Platform** - Works on Windows, macOS, and Linux  
✅ **No Browser Required** - Self-contained desktop app experience  
✅ **Resizable** - Window can be resized and minimized  
✅ **Professional** - Looks and feels like a native application  

## Technology

Uses **pywebview** - a lightweight library that:
- Wraps native webview components (smaller than Electron)
- Works on Windows (WebView2), macOS (WKWebView), and Linux (WebKitGTK)
- Embeds the FastAPI server internally
- Provides native window controls

## Building

### Windows
```batch
build_windows_standalone.bat
```

### Linux
```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

### macOS
```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

## Usage

1. **Run the executable:**
   - Windows: Double-click `PhoenixDashboard-Windows-x64.exe`
   - Linux: `chmod +x PhoenixDashboard-Linux-*` then `./PhoenixDashboard-Linux-*`
   - macOS: Double-click `PhoenixDashboard.app`

2. **Native window opens:**
   - A desktop window appears (not a browser)
   - Window is resizable and can be minimized
   - All dashboard features work normally

3. **Close the window:**
   - Click the X button or close normally
   - Application shuts down cleanly

## Window Features

- **Size:** 1400x900 pixels (default)
- **Minimum:** 800x600 pixels
- **Resizable:** Yes
- **Fullscreen:** No (can be added if needed)
- **Title:** "Phoenix Dashboard"

## Technical Details

- Server runs on `127.0.0.1:8000` (or next available port)
- Webview loads the dashboard from the local server
- Server shuts down when window is closed
- No console window needed (runs in background)

## Requirements

- **Windows:** WebView2 (included in Windows 11, can be installed on Windows 10)
- **macOS:** WKWebView (included in macOS)
- **Linux:** WebKitGTK (usually pre-installed, or: `sudo apt install webkit2gtk-4.0`)

## Advantages Over Browser

✅ **Native feel** - Looks like a real desktop app  
✅ **No browser tabs** - Clean, focused experience  
✅ **Better integration** - Can add native menus, notifications, etc.  
✅ **Smaller size** - Uses native webview, not full browser  
✅ **More control** - Can customize window behavior  

## Future Enhancements

Possible additions:
- System tray icon
- Native menus
- Keyboard shortcuts
- Window state persistence
- Custom window styling

Enjoy your native desktop application! 🚀

