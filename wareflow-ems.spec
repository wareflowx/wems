"""
PyInstaller spec file for Wareflow EMS

This configuration builds a Windows executable (.exe) from the Python application.
It packages all dependencies, data files, and resources into a single file.
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Bundle all external data files
datas = [
    ('build/assets/icon.ico', '.'),  # Application icon
]

# Collect all data files from packages
datas += collect_data_files('customtkinter')
datas += collect_data_files('peewee')

# Collect all submodules to ensure complete imports
hiddenimports = [
    'customtkinter',
    'customtkinter.windows',
    'peewee',
    'PIL',
    'PIL._tkinter_finder',
    'openpyxl',
    'openpyxl.cell._writer',
    'tkinter',
    'tkinter.ttk',
    'sqlite3',
]

# Collect submodules
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('peewee')

# Exclude unnecessary modules
excludes = [
    'tests',
    'pytest',
    'pytest_asyncio',
    'unittest',
    'distutils',
]

block_cipher = None

a = Analysis(
    ['src/main.py'],  # Entry point
    pathex=[],
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

# Remove tests from the build
a.datas = [x for x in a.datas if 'tests' not in x[0].lower()]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Wareflow EMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='build/assets/icon.ico',  # Application icon
)
