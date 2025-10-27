#!/bin/bash
# Build script for standalone macOS application

set -e

echo "Building standalone macOS application..."

# Create a clean environment
rm -rf build/ dist/ *.spec

# Create PyInstaller spec file
cat > phoenix.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('app/models.py', 'app'),
        ('app/sse.py', 'app'),
        ('app/data.py', 'app'),
        ('src/realtime/eth_feed.py', 'src/realtime'),
    ],
    hiddenimports=[
        'app.main',
        'app.models',
        'app.sse',
        'app.data',
        'src.realtime.eth_feed',
        'uvicorn',
        'fastapi',
        'jinja2',
        'sse_starlette',
        'web3',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Phoenix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Phoenix',
)

app = BUNDLE(
    coll,
    name='Phoenix.app',
    icon=None,
    bundle_identifier='com.phoenix.dashboard',
)
EOF

# Install PyInstaller if not already installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the application
echo "Building app bundle..."
pyinstaller phoenix.spec --clean

echo "✓ Build complete!"
echo ""
echo "You can find the standalone app at: dist/Phoenix.app"
echo ""
echo "To run the app, you can either:"
echo "  1. Double-click Phoenix.app in the dist/ folder"
echo "  2. Or run: open dist/Phoenix.app"
echo ""
echo "Note: The first time you open it, macOS may show a security warning."
echo "     Right-click the app and select 'Open' to bypass this warning."

