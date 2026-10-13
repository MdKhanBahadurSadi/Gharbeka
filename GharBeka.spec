# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for GharBeka Windows Desktop Application.

Builds a standalone Windows executable with embedded version info, custom icon,
bundled assets, and essential PySide6 Qt libraries while excluding test suites.
"""

import sys
from pathlib import Path

block_cipher = None

# Project paths
spec_root = Path.cwd()
assets_dir = spec_root / "assets"
version_file = spec_root / "version_info.txt"
icon_file = spec_root / "assets" / "icon.ico"

# Data assets to bundle into sys._MEIPASS / executable directory
datas = []
if assets_dir.exists():
    datas.append(('assets', 'assets'))

# Exclude test frameworks and non-runtime tools to minimize bundle size
excludes = [
    'pytest',
    '_pytest',
    'unittest',
    'tests',
    'tkinter',
    'sqlite3',
    'pydoc',
]

# Hidden imports necessary for dynamic PySide6 integration
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'ctypes',
    'ctypes.wintypes',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# 1. Standalone One-File Executable: dist/GharBeka.exe
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GharBeka',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(version_file) if version_file.exists() else None,
    icon=str(icon_file) if icon_file.exists() else None,
)

# 2. Diagnostic One-Directory Distribution: dist/GharBeka_onedir/
exe_onedir = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GharBeka_diag',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    version=str(version_file) if version_file.exists() else None,
    icon=str(icon_file) if icon_file.exists() else None,
)

coll = COLLECT(
    exe_onedir,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='GharBeka_onedir',
)
