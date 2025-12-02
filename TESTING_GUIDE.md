# Quick Testing Guide

## ✅ Build Complete!

Your Windows standalone executable has been built successfully!

## Files Created

- **`downloads/PhoenixDashboard-Windows-x64.exe`** - Standalone executable (ready to run!)
- **`downloads/windows/PhoenixDashboard-Windows-x64.zip`** - ZIP package with README

## How to Test

### Option 1: Run the Executable Directly

1. Navigate to the `downloads` folder
2. Double-click `PhoenixDashboard-Windows-x64.exe`
3. Your browser should automatically open to `http://127.0.0.1:8000`
4. Test the dashboard:
   - Navigate between pages
   - Check charts and metrics
   - Click "📥 Downloads" in the footer or top nav
   - Verify all features work
5. To stop: Press `Ctrl+C` in the console window

### Option 2: Test from ZIP Package

1. Extract `downloads/windows/PhoenixDashboard-Windows-x64.zip`
2. Open the extracted folder
3. Double-click `PhoenixDashboard.exe`
4. Test as above

### Option 3: Test the Downloads Page

1. Start your regular Phoenix Dashboard server:
   ```batch
   python app.py
   ```
   Or:
   ```batch
   python start.py
   ```

2. Navigate to: `http://localhost:8000/downloads`
   - Or click "📥 Downloads" in the footer/top nav

3. You should see:
   - Download links for all platforms
   - Installation instructions
   - Build information

## What to Check

- [ ] Executable runs without errors
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] All pages work (Dashboard, Explorer, Bots, etc.)
- [ ] Charts and metrics display
- [ ] Downloads page is accessible
- [ ] Can stop cleanly with Ctrl+C

## Troubleshooting

**Browser doesn't open:**
- Manually navigate to `http://127.0.0.1:8000`
- Check the console for the actual port number

**"Windows protected your PC" warning:**
- Click "More info" → "Run anyway"
- This is normal for unsigned executables

**Antivirus blocks it:**
- Add an exception for the downloads folder
- PyInstaller executables sometimes trigger false positives

## Next Steps

1. ✅ Test the executable (you're doing this now!)
2. Test on a clean Windows machine/VM (without Python)
3. Build for Linux when ready: `./build_linux_standalone.sh`
4. Build installer (requires NSIS): `build_windows_installer.bat`

## Build Info

- **Version:** 0.1.0.3
- **Build Number:** 3
- **Timestamp:** 20251201143348
- **Full Version:** 0.1.0.3.20251201143348

Enjoy testing! 🚀



