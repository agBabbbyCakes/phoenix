# Windows SmartScreen Warning - How to Fix

## What You're Seeing

When you try to run `PhoenixDashboard-Windows-x64.exe`, Windows shows:
> **"Windows protected your PC - Microsoft Defender SmartScreen prevented an unrecognized app from starting"**

## Why This Happens

This is **normal and expected** for PyInstaller executables because:
- The executable is not code-signed (requires a paid certificate)
- Windows doesn't recognize the publisher
- It's a security feature to protect users

**The executable is safe** - it's your own code packaged with PyInstaller.

## How to Run It (3 Options)

### Option 1: Click "More info" (Recommended)

1. In the SmartScreen popup, click **"More info"**
2. Click **"Run anyway"** button
3. The app will launch

**Note:** After running it once, Windows usually remembers and won't show the warning again.

### Option 2: Add Exception to Windows Defender

1. Open **Windows Security** (search "Windows Security" in Start menu)
2. Go to **Virus & threat protection**
3. Click **Manage settings** under Virus & threat protection settings
4. Scroll down to **Exclusions**
5. Click **Add or remove exclusions**
6. Click **Add an exclusion** → **Folder**
7. Select your `downloads` folder (or the specific file)

### Option 3: Unblock the File

1. Right-click `PhoenixDashboard-Windows-x64.exe`
2. Select **Properties**
3. At the bottom, check **"Unblock"** (if available)
4. Click **OK**
5. Try running it again

## Quick Fix (Easiest)

**Just click "More info" → "Run anyway"** in the SmartScreen popup.

After the first run, Windows usually remembers and won't show the warning again for this file.

## For Distribution

If you're sharing this with others, they'll see the same warning. You can:

1. **Tell them it's safe** - it's a PyInstaller executable
2. **Provide instructions** - include this guide
3. **Code sign it** (optional, requires certificate):
   - Purchase a code signing certificate (~$200-400/year)
   - Sign with: `signtool sign /f certificate.pfx PhoenixDashboard.exe`

## Alternative: Run from ZIP

Users can also:
1. Extract the ZIP file
2. Run from the extracted folder
3. Sometimes this reduces the warning

## Summary

✅ **The warning is normal** - PyInstaller executables aren't signed  
✅ **The file is safe** - it's your own code  
✅ **Click "More info" → "Run anyway"** to proceed  
✅ **Windows will remember** after first run  

This is a Windows security feature, not a problem with your build! 🚀



