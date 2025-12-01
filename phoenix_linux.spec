# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Phoenix Dashboard - Linux (including Raspberry Pi)

import sys
from pathlib import Path

block_cipher = None

# Get project root
project_root = Path(SPECPATH).parent if 'SPECPATH' in globals() else Path.cwd()

# Collect all data files
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]

# Hidden imports
hiddenimports = [
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.logging',
    'fastapi',
    'fastapi.templating',
    'fastapi.staticfiles',
    'fastapi.responses',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'jinja2',
    'sse_starlette',
    'sse_starlette.sse',
    'app',
    'app.main',
    'app.sse',
    'app.data',
    'app.models',
    'src.realtime.eth_feed',
]

a = Analysis(
    ['standalone_launcher.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'watchdog',
        'watchgod',
        'wsproto',
        'python_socks',
        'eth_tester',
        'a2wsgi',
        'multipart',
        'orjson',
        'ujson',
        'cryptography.hazmat',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhoenixDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

