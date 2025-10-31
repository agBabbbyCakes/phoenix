# Briefcase Commands Guide

## Prerequisites

Make sure you have Python 3.11+ and Briefcase installed:

```bash
# Install Briefcase (if not already installed)
pip install briefcase
```

## Initial Setup

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /Users/agworkywork/phoenix

# Install Python dependencies
pip install -r requirements.txt
# OR if using uv
uv pip install -r requirements.txt
```

### 2. Create Briefcase App Structure

```bash
# Create the app structure for your platform
# For macOS:
briefcase create macOS

# For Windows (if on Windows or cross-compiling):
briefcase create windows

# For Linux (if on Linux or cross-compiling):
briefcase create linux
```

### 3. Development Mode

```bash
# Run in development mode (runs the app with live code)
briefcase dev
```

This will:
- Start the Phoenix server
- Open the GUI window
- Allow you to test the app before building

## Building for Production

### macOS App Bundle

```bash
# Build the macOS app
briefcase build macOS

# Package as .app bundle
briefcase package macOS

# The .app bundle will be in: dist/macOS/Phoenix Dashboard.app
```

### Windows MSI Installer

```bash
# Build the Windows app
briefcase build windows

# Create MSI installer
briefcase package windows

# The installer will be in: dist/windows/Phoenix Dashboard.msi
```

### Linux AppImage

```bash
# Build the Linux app
briefcase build linux

# Create AppImage
briefcase package linux

# The AppImage will be in: dist/linux/Phoenix Dashboard.AppImage
```

## Clean Build (If Something Goes Wrong)

If you encounter issues during build, clean and rebuild:

```bash
# Remove build artifacts
rm -rf build/
rm -rf dist/

# Clean Briefcase cache (optional)
rm -rf ~/.briefcase/

# Recreate the app structure
briefcase create macOS  # or windows/linux

# Rebuild
briefcase build macOS

# Rebuild and package
briefcase package macOS
```

## Quick Reference

### All Platforms at Once

```bash
# Clean everything
rm -rf build/ dist/

# Create for all platforms (run on each platform)
briefcase create macOS
briefcase create windows
briefcase create linux

# Build for all platforms
briefcase build macOS
briefcase build windows
briefcase build linux

# Package for all platforms
briefcase package macOS
briefcase package windows
briefcase package linux
```

### Update After Code Changes

```bash
# Update the app code in the build
briefcase update macOS

# Rebuild
briefcase build macOS
briefcase package macOS
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, the app will automatically find a free port.

### Dependencies Issues

If you get dependency errors:

```bash
# Clean and recreate
rm -rf build/
briefcase create macOS
```

### Template Issues

If you get template errors, update Briefcase:

```bash
pip install --upgrade briefcase
```

