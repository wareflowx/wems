"""
PyInstaller spec file for Wareflow EMS

This configuration builds a Windows executable (.exe) from the Python application.
It packages all dependencies, data files, and resources into a single file.
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get project root directory
# __file__ is not available in spec context, use sys.argv[0]
spec_file_path = Path(sys.argv[0]).resolve() if len(sys.argv) > 0 else Path.cwd()
project_root = spec_file_path.parent

# Bundle all external data files
datas = [
    ('build/assets/icon.ico', '.'),  # Application icon
    ('src', 'src'),  # Include entire src directory
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
    # 'magic',  # Removed: causes PyInstaller crash
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
    ['src/main_exe.py'],  # Entry point for PyInstaller
    pathex=[str(project_root)],  # Add project root to path so PyInstaller can find src package
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['src/pyi_rthook_src.py'],  # Runtime hook to fix src imports
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
