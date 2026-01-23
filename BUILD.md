# Building Wareflow EMS Standalone Executables

This guide explains how to build standalone executables for Wareflow Employee Management System that don't require Python installation.

## Overview

Wareflow EMS can be distributed as standalone executables using PyInstaller. These executables bundle all dependencies and can run on any system without requiring Python installation.

### Available Builds

- **GUI Version (wems)**: Full-featured desktop application with CustomTkinter GUI
- **CLI Version (wems-cli)**: Command-line interface for automation and scripting

### Supported Platforms

- **Windows 10/11**: `.exe` executable
- **Linux (Ubuntu 20.04+, Debian 11+)**: Binary executable
- **macOS**: (Coming soon - pending code signing setup)

## Prerequisites

### Required Tools

1. **Python 3.14+** (for building only, not required for running the executable)
2. **uv** - Fast Python package installer
   ```bash
   pip install uv
   ```
3. **PyInstaller** - Bundling tool
   ```bash
   uv pip install pyinstaller
   ```

### System Requirements for Building

- **Windows**: Windows 10 or later with Visual C++ Redistributable
- **Linux**: Build essentials (gcc, g++, make)
- **Disk Space**: ~500 MB for dependencies and build artifacts

## Quick Start

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/wareflowx/wareflow-ems.git
cd wareflow-ems

# Install dependencies
uv sync --dev

# Install PyInstaller
uv pip install pyinstaller
```

### Build Executables

```bash
# Build GUI version (default)
python build/build.py

# Build CLI version
python build/build.py --cli

# Build both versions
python build/build.py --all

# Clean build (removes old artifacts)
python build/build.py --clean

# Skip tests (faster for development)
python build/build.py --skip-tests
```

### Build Artifacts

Built executables are located in `dist/`:

```
dist/
├── wems/
│   ├── wems.exe              # Windows GUI executable
│   └── [supporting files]
├── wems-cli/
│   ├── wems-cli.exe          # Windows CLI executable
│   └── [supporting files]
├── wems-version.txt          # Version info
└── wems-cli-version.txt      # Version info
```

## Detailed Build Options

### GUI Build

```bash
python build/build.py
```

Creates a GUI application with:
- CustomTkinter interface
- Full feature set
- No console window
- Double-click to run

**Output**: `dist/wems/wems.exe` (Windows) or `dist/wems/wems` (Linux)

### CLI Build

```bash
python build/build.py --cli
```

Creates a command-line application with:
- All CLI commands
- Works in terminals
- Smaller file size
- Scriptable

**Output**: `dist/wems-cli/wems-cli.exe` (Windows) or `dist/wems-cli/wems-cli` (Linux)

### Build Both Versions

```bash
python build/build.py --all
```

Builds both GUI and CLI versions in sequence.

### Clean Build

```bash
python build/build.py --clean
```

Removes all build artifacts before building, ensuring a fresh build.

### Specify Version

```bash
python build/build.py --version 1.2.3
```

Overrides the automatic version detection.

## Build Spec Files

### wems.spec (GUI)

Configuration for the GUI executable:
- Entry point: `src/main.py`
- Includes: CustomTkinter, GUI modules, all dependencies
- Windowed: No console shown
- Icon: `build/assets/icon.ico`

### wems-cli.spec (CLI)

Configuration for the CLI executable:
- Entry point: `src/cli_main.py`
- Includes: CLI modules, excludes GUI frameworks
- Console: Shows terminal output
- Smaller size: GUI modules excluded

## Verification

### Checksums

Each build generates SHA256 checksums:

```bash
# Windows
certutil -hashify SHA256 dist/wems/wems.exe

# Linux
sha256sum dist/wems/wems
```

Checksums are saved as `dist/wems.exe.sha256` for verification.

### Version Info

Version information is injected during build:

```bash
cat dist/wems-version.txt
```

Output:
```
Wareflow Employee Management System
Version: 1.2.3
Build Type: GUI
Build Date: 2025-01-23T12:00:00
Platform: win32
Python: 3.14.2
```

## Testing Builds

### Quick Smoke Test

```bash
# Windows
dist\wems\wems.exe

# Linux
chmod +x dist/wems/wems
./dist/wems/wems
```

### Test CLI Commands

```bash
# Windows
dist\wems-cli\wems-cli.exe --help

# Linux
chmod +x dist/wems-cli/wems-cli
./dist/wems-cli/wems-cli --help
```

### Test GUI Functionality

1. Launch the executable
2. Verify main window opens
3. Try adding an employee
4. Check database operations
5. Test Excel import/export

## Distribution

### Preparing for Release

1. **Run full build**:
   ```bash
   python build/build.py --all --clean
   ```

2. **Verify checksums**:
   ```bash
   cat dist/wems/*.sha256
   cat dist/wems-cli/*.sha256
   ```

3. **Test on clean system**:
   - Copy to a machine without Python
   - Verify it runs correctly
   - Test all major features

4. **Package for distribution**:
   ```bash
   # Create release package
   mkdir release
   cp dist/wems/wems.exe release/
   cp dist/wems-cli/wems-cli.exe release/
   cat dist/wems/*.sha256 > release/checksums.txt
   cat dist/wems-cli/*.sha256 >> release/checksums.txt
   cp README.md release/
   cp LICENSE release/
   ```

### GitHub Releases

Automated builds via GitHub Actions:

1. Push a tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. GitHub Actions automatically:
   - Builds executables for all platforms
   - Runs tests
   - Generates checksums
   - Creates GitHub Release
   - Uploads artifacts

3. Download from:
   ```
   https://github.com/wareflowx/wareflow-ems/releases
   ```

## Troubleshooting

### Build Fails

**Issue**: `ModuleNotFoundError: No module named 'customtkinter'`

**Solution**:
```bash
uv sync
uv pip install customtkinter
```

**Issue**: `ImportError: DLL load failed`

**Solution**: Install Visual C++ Redistributable:
- Download from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Install and restart

**Issue**: Icon not found

**Solution**:
```bash
python build/create_icon.py
```

### Executable Won't Run

**Issue**: Double-clicking does nothing

**Solution**: Run from command line to see error:
```bash
# Windows
cd dist\wems
wems.exe

# Linux
cd dist/wems
./wems
```

**Issue**: "Application failed to start"

**Solution**:
- Verify all supporting files are present
- Check antivirus isn't blocking it
- Try running as administrator

**Issue**: Database errors

**Solution**:
- Ensure data directory exists
- Check file permissions
- Verify database isn't corrupted

### File Size Issues

**Issue**: Executable is too large (> 150 MB)

**Solution**:
1. Check what's included in the spec file
2. Add more packages to `excludes` list
3. Use UPX compression (enabled by default)
4. Consider one-file vs directory build

**Issue**: Executable is too small (< 20 MB)

**Solution**:
- Something likely failed during build
- Check build logs for errors
- Verify all dependencies were bundled

### Platform-Specific Issues

#### Windows

**SmartScreen Warning**: Windows shows "Unrecognized app" warning

**Solution**: This is expected for unsigned executables. Users need to click "More info" → "Run anyway".

**Antivirus Blocks**: Antivirus software flags the executable

**Solution**:
- Add to antivirus exclusions
- Submit to Microsoft SmartScreen for whitelist
- Sign the executable (code signing certificate required)

#### Linux

**Permission Denied**: Can't execute the binary

**Solution**:
```bash
chmod +x dist/wems/wems
```

**Missing Libraries**: Error about missing `.so` files

**Solution**:
```bash
# Install missing dependencies
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

#### macOS

**Gatekeeper Blocks**: "can't be opened because it is from an unidentified developer"

**Solution**: Code signing is required for distribution. This is not yet implemented.

## Advanced Configuration

### Customizing the Icon

1. Edit `build/create_icon.py`
2. Change colors, text, or design
3. Regenerate icons:
   ```bash
   python build/create_icon.py
   ```

### Modifying Spec Files

Edit `build/wems.spec` or `build/wems-cli.spec`:

**Add hidden imports**:
```python
hiddenimports = [
    "your.module",
    "another.module",
]
```

**Exclude packages**:
```python
excludes = [
    "unwanted.package",
]
```

**Include data files**:
```python
datas = [
    ("path/to/data", "data"),
]
```

### One-File Build

For a single-file executable (not recommended - slower startup):

In spec file, change:
```python
exe = EXE(
    ...
    exclude_binaries=False,  # Changed from True
    ...
)

# Remove the COLLECT section
```

### Compression

Enable UPX compression (enabled by default):
```python
exe = EXE(
    ...
    upx=True,
    upx_exclude=[],
    ...
)
```

## CI/CD Integration

The `.github/workflows/build.yml` workflow automatically builds executables on:

1. **Git tags**: Push `v*.*.*` tag to trigger build
2. **Manual trigger**: Use GitHub Actions "Run workflow" button

The workflow:
- Builds on Windows and Linux
- Runs tests
- Generates checksums
- Creates GitHub Release
- Uploads artifacts

## Performance Optimization

### Reduce File Size

1. **Exclude unused modules**:
   ```python
   excludes = ["matplotlib", "numpy", "pandas"]
   ```

2. **Use UPX compression**: Enabled by default

3. **Strip symbols**:
   ```python
   exe = EXE(
       ...
       strip=True,
       ...
   )
   ```

### Improve Startup Time

1. **Use directory build instead of one-file**
   - One-file: Must unpack every run
   - Directory: Faster startup

2. **Optimize imports**:
   - Remove unused imports in source code
   - Lazy load heavy modules

## Best Practices

1. **Always test on clean system**
   - Build on development machine
   - Test on machine without Python
   - Verify all features work

2. **Version your builds**
   - Use semantic versioning
   - Tag releases in git
   - Keep build artifacts

3. **Generate checksums**
   - Always provide SHA256 checksums
   - Document in release notes
   - Users can verify integrity

4. **Keep builds reproducible**
   - Use same Python version
   - Lock dependency versions
   - Document build environment

5. **Test before release**
   - Run full test suite
   - Manual testing of GUI
   - Test on target platforms

## Support

For issues or questions:
- **Documentation**: See [docs/](docs/)
- **GitHub Issues**: [Report a problem](https://github.com/wareflowx/wareflow-ems/issues)
- **Discussions**: [Ask a question](https://github.com/wareflowx/wareflow-ems/discussions)

## Related Documentation

- [INSTALL.md](INSTALL.md) - Installation guide
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) - Release process
- [pyproject.toml](pyproject.toml) - Project configuration
