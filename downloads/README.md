# Phoenix Dashboard - Standalone Downloads

This directory contains standalone executable builds of Phoenix Dashboard for different platforms.

## Windows SmartScreen Warning

**If you see "Windows protected your PC" when running the .exe:**

This is normal for PyInstaller executables. The file is safe - it's your own code.

**To run it:**
1. Click **"More info"** in the warning
2. Click **"Run anyway"**
3. Windows will remember after the first run

See `WINDOWS_SMARTScreen_FIX.md` in the project root for more details.

## Available Builds

- **Windows**: `PhoenixDashboard-Windows-x64.exe` - Double-click to run
- **macOS**: `PhoenixDashboard-macOS.zip` - Extract and run the .app bundle
- **Linux**: `PhoenixDashboard-Linux-x86_64` - Make executable and run
- **Raspberry Pi**: `PhoenixDashboard-RaspberryPi-armv7l` - Make executable and run

## Building

To build these executables yourself, use the platform-specific build scripts:

- Windows: `build_windows_standalone.bat`
- macOS: `build_macos_standalone.sh`
- Linux: `build_linux_standalone.sh`
- Raspberry Pi: `build_raspberrypi_standalone.sh`

## Usage

All standalone builds:
1. Include all dependencies (no Python installation needed)
2. Automatically open your browser when started
3. Run a local web server on port 8000 (or next available port)
4. Can be stopped with Ctrl+C

## Raspberry Pi Notes

For Raspberry Pi, you can:
- Run the executable directly on the Pi
- Access the dashboard from other devices on your network using the Pi's IP address
- Set up as a systemd service for automatic startup

Example systemd service (`/etc/systemd/system/phoenix-dashboard.service`):

```ini
[Unit]
Description=Phoenix Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/phoenix
ExecStart=/home/pi/phoenix/downloads/PhoenixDashboard-RaspberryPi-armv7l
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable phoenix-dashboard
sudo systemctl start phoenix-dashboard
```

