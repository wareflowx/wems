# Build Directory

This directory contains build configuration and scripts for creating standalone executables of the Wareflow Employee Management System.

## Files

- `wems.spec` - PyInstaller spec file for building executables
- `build.py` - Python build script with test execution and checksum generation
- `README.md` - This file

## Building Locally

### Prerequisites

```bash
# Install build dependencies
pip install pyinstaller

# Or using uv
uv pip install pyinstaller
```

### Build Commands

```bash
# Standard build (runs tests, builds executable, generates checksums)
python build/build.py

# Clean build (removes build/dist directories first)
python build/build.py --clean

# Build with specific version
python build/build.py --version v1.2.3

# Build without running tests
python build/build.py --skip-tests
```

### Direct PyInstaller Build

```bash
# Build using spec file
uv run pyinstaller build/wems.spec --clean --noconfirm

# Output will be in dist/wems/
```

## CI/CD Builds

The project uses GitHub Actions for automated builds:

### Triggering Builds

**Automatic (on tag push):**
```bash
git tag v1.2.3
git push origin v1.2.3
```

**Manual (via GitHub Actions):**
1. Go to Actions tab in GitHub
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Enter version (e.g., v1.2.3)
5. Optionally enable GitHub release creation

### Build Matrix

Builds are created for multiple platforms:
- Windows (`wems-windows.exe`)
- Linux (`wems-linux`)
- macOS (disabled until proper setup)

### Artifacts

Each build produces:
1. **Executable** - Standalone application binary
2. **Checksum** - SHA256 hash for verification
3. **GitHub Release** - Automatic release with changelog (on tags)

## Build Process Flow

1. **Checkout** - Get source code from git
2. **Setup** - Install Python and dependencies
3. **Test** - Run test suite to ensure quality
4. **Build** - Create executable with PyInstaller
5. **Checksum** - Generate SHA256 hashes
6. **Upload** - Save artifacts for download
7. **Release** - Create GitHub release (if tag pushed)

## Version Detection

The build system determines version from:
1. Git tags (e.g., `v1.2.3`) - preferred for releases
2. Git commit hash - for dev builds
3. Fallback to `unknown` if git unavailable

## PyInstaller Spec File

The `wems.spec` file defines:

- **Entry point**: `src/main.py`
- **Hidden imports**: All required dependencies
- **Data files**: UI assets, utilities, state
- **Excludes**: Unnecessary packages (tkinter, numpy, etc.)
- **Output**: Single directory with executable and dependencies

### Customizing the Spec File

To add additional data files:
```python
datas = [
    (str(SRC_DIR / "ui_ctk"), "ui_ctk"),
    (str(SRC_DIR / "utils"), "utils"),
    # Add your data files here
    (str(ROOT_DIR / "data"), "data"),
]
```

To add hidden imports:
```python
hiddenimports = [
    "customtkinter",
    # Add your imports here
    "your_module",
]
```

## Troubleshooting

### Build Fails with Import Errors

Add missing imports to `hiddenimports` list in `wems.spec`:
```python
hiddenimports = [
    "your_missing_module",
]
```

### Executable Crashes on Startup

1. Check console output (set `console=True` in spec file)
2. Verify all data files are included in `datas`
3. Test with debug mode:
   ```bash
   pyinstaller --debug=all build/wems.spec
   ```

### Missing DLL Errors on Windows

Some packages may require additional DLL files. Add them to `binaries` in spec:
```python
binaries = [
    ("path/to/dll.dll", "."),
]
```

### Large Executable Size

To reduce size:
1. Enable UPX compression (already enabled)
2. Exclude unused packages in `excludes` list
3. Use `--onefile` mode (current: `--onedir`)

## Best Practices

1. **Always run tests before building** - Ensures quality
2. **Use git tags for releases** - Automatic version detection
3. **Verify checksums** - Ensure build integrity
4. **Test executable on clean system** - Catch missing dependencies
5. **Keep spec file updated** - Reflect code changes

## Release Checklist

Before creating a release:

- [ ] All tests pass
- [ ] Version updated in `pyproject.toml`
- [ ] Git tag created (e.g., `v1.2.3`)
- [ ] Changelog updated
- [ ] Build tested locally
- [ ] Executable runs on clean system
- [ ] Checksums verified
