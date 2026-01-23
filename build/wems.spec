# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Wareflow Employee Management System.

This spec file defines how to bundle the application into a standalone executable.
It includes all necessary dependencies, data files, and configuration.

Usage:
    pyinstaller wems.spec

Or via CI/CD:
    uv run pyinstaller build/wems.spec
"""

import os
import sys
from pathlib import Path

# Get the root directory of the project
block_cipher = None
ROOT_DIR = Path(SPECPATH)
SRC_DIR = ROOT_DIR / "src"

# Collect all hidden imports
hiddenimports = [
    "customtkinter",
    "PIL",
    "peewee",
    "openpyxl",
    "openpyxl.cell._writer",
    "excel_import.template_generator",
    "utils.config",
    "utils.logging_config",
    "database.connection",
    "database.migration_model",
    "employee.models",
    "employee.calculations",
    "employee.validators",
    "employee.queries",
    "employee.alerts",
    "lock.manager",
    "lock.models",
]

# Data files to include
datas = [
    (str(SRC_DIR / "ui_ctk"), "ui_ctk"),
    (str(SRC_DIR / "utils"), "utils"),
    (str(SRC_DIR / "state"), "state"),
]

# Binary excludes (exclude unnecessary files)
binaries_excludes = []

# Import exclusions
excludes = [
    "tkinter",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "IPython",
]

# Analysis
a = Analysis(
    [str(SRC_DIR / "main.py")],
    pathex=[str(ROOT_DIR)],
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

# Remove unnecessary files from the executable
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="wems" if sys.platform != "win32" else "wems",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True to debug console output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available: str(ROOT_DIR / "assets" / "icon.ico")
)

# Collect all binaries and Python files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wems",
)
