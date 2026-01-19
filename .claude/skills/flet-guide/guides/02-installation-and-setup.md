# Installation and Setup

## System Requirements

Before installing Flet, ensure your system meets these requirements:

### Python Version
- **Python 3.10 or higher** is required
- Python 3.12+ is recommended for best performance

Check your Python version:
```bash
python --version
# or
python3 --version
```

### Operating Systems

| Platform | Minimum Version | Notes |
|----------|----------------|-------|
| Windows | Windows 10 (64-bit) | Windows 11 recommended |
| macOS | macOS 11 (Big Sur) | Intel and Apple Silicon supported |
| Linux | Debian 11+ or Ubuntu 20.04+ | Other distros may work |
| Web | Any modern browser | Chrome, Firefox, Safari, Edge |

### WSL Support
Flet works on Windows Subsystem for Linux 2 (WSL 2), but you may encounter display issues. If you get a "cannot open display" error, ensure WSLg is properly configured.

## Installation Methods

### Method 1: Standard pip Installation (Recommended)

For most users, the standard pip installation is sufficient:

```bash
pip install flet
```

This installs the core Flet package with desktop support.

### Method 2: Full Feature Installation

To enable all features including mobile build tools:

```bash
pip install "flet[all]"
```

The `[all]` extra includes:
- Mobile build dependencies
- Additional image format support
- All optional dependencies

### Method 3: Using UV (Fast Package Manager)

[UV](https://docs.astral.sh/uv/) is a modern, fast Python package manager written in Rust:

```bash
# Install UV if you haven't already
pip install uv

# Create a new project
uv init --python='>=3.10' my-flet-app
cd my-flet-app

# Install Flet
uv pip install flet
```

UV is significantly faster than pip and is ideal for development workflows.

## Virtual Environment Setup

Using virtual environments is **strongly recommended** to isolate dependencies.

### Using Python's Built-in venv

```bash
# Create project directory
mkdir my-flet-app
cd my-flet-app

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install Flet
pip install flet
```

### Using Conda

If you're a Conda user:

```bash
# Create a new environment
conda create -n flet-env python=3.11

# Activate the environment
conda activate flet-env

# Install Flet
pip install flet
```

## Verifying Installation

After installation, verify that Flet is correctly installed:

```bash
python -c "import flet; print(flet.__version__)"
```

You should see the version number printed.

Test with a simple app:

```python
# test.py
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("Flet is working!"))

ft.run(main)
```

Run it:
```bash
python test.py
```

A window should appear with the text "Flet is working!".

## Flet CLI Installation

Flet includes a command-line interface for building, running, and packaging apps.

The CLI is automatically installed with Flet. Verify it:

```bash
flet --version
```

### Essential CLI Commands

| Command | Description |
|---------|-------------|
| `flet run <file>` | Run app in desktop mode |
| `flet run --web <file>` | Run app in web browser |
| `flet build apk` | Build Android APK |
| `flet build ipa` | Build iOS IPA |
| `flet build macos` | Build macOS app |
| `flet build windows` | Build Windows executable |
| `flet create <name>` | Create new project from template |

## IDE Setup

### Visual Studio Code

1. **Install the Python extension** from the marketplace
2. **Select Python interpreter** - Your virtual environment
3. **Install recommended extensions**:
   - Python
   - Pylance (language server)
   - Python Test Explorer

Configure `settings.json` for Flet development:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

### PyCharm

1. **Create new project** with your virtual environment
2. **Mark source root** - Right-click your source folder → "Mark Directory as" → "Sources Root"
3. **Enable auto-completion** - Ensure PyCharm's Python interpreter is set to your venv

### Jupyter Notebook

Flet doesn't run well in Jupyter notebooks due to its event loop requirements. Use `.py` files instead.

## Project Structure

A typical Flet project structure:

```
my-flet-app/
├── .venv/                    # Virtual environment
├── assets/                   # Images, fonts, icons
│   ├── images/
│   └── icons/
├── src/                      # Source code
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── views/               # UI components
│   │   ├── home.py
│   │   └── settings.py
│   ├── models/              # Data models
│   └── services/            # Business logic
├── tests/                    # Tests
│   └── test_main.py
├── requirements.txt          # Dependencies
├── pyproject.toml           # Project config (optional)
└── README.md
```

### requirements.txt

Create a `requirements.txt` file for reproducible builds:

```
flet>=0.21.0
requests>=2.31.0
python-dotenv>=1.0.0
```

Install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Running Flet Apps

### Desktop Mode

Run in a native OS window:

```bash
flet run main.py
# or
python main.py
```

### Web Mode

Run in a web browser:

```bash
flet run --web main.py
```

The app will open at `http://localhost:8550` by default.

### Specify Port

```bash
flet run --web --port 8080 main.py
```

### Mobile Testing

Test on Android emulator or connected device:

```bash
# List connected devices/emulators
flet devices

# Run on specific device
flet run -d emulator-5554 main.py
```

## Environment Variables

Flet respects several environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLET_WEB_PORT` | Web server port | 8550 |
| `FLET_WEB_BROWSER_OPEN` | Auto-open browser | true |
| `FLET_ASSETS_PATH` | Custom assets directory | ./assets |
| `FLET_DEBUG` | Enable debug mode | false |

Set them in your shell or `.env` file:

```bash
# Linux/macOS
export FLET_WEB_PORT=9000

# Windows (PowerShell)
$env:FLET_WEB_PORT="9000"

# Windows (Command Prompt)
set FLET_WEB_PORT=9000
```

## Troubleshooting

### Import Error: No module named 'flet'

**Problem**: Python can't find the Flet module.

**Solutions**:
1. Ensure your virtual environment is activated
2. Verify Flet is installed: `pip list | grep flet`
3. Reinstall: `pip install --force-reinstall flet`

### Display Issues on Linux

**Problem**: `cannot open display` error.

**Solutions**:
1. Install X11: `sudo apt-get install xvfb`
2. Run with virtual display: `xvfb-run python main.py`
3. Use web mode instead: `flet run --web main.py`

### Port Already in Use

**Problem**: Address already in use error.

**Solutions**:
1. Find and kill the process using the port
2. Use a different port: `flet run --web --port 9000 main.py`

### macOS Gatekeeper Warning

**Problem**: App can't be opened because it's from an unidentified developer.

**Solution**:
```bash
xattr -cr /path/to/Flet.app
```

## Upgrading Flet

To upgrade to the latest version:

```bash
pip install --upgrade flet
```

Or with UV:

```bash
uv pip install --upgrade flet
```

## Production Deployment Setup

For production deployments, consider:

1. **Pin versions** in requirements.txt:
   ```
   flet==0.21.0
   ```

2. **Use separate environments**:
   ```bash
   # Development
   python -m venv .venv-dev

   # Production
   python -m venv .venv-prod
   ```

3. **Freeze dependencies**:
   ```bash
   pip freeze > requirements-lock.txt
   ```

## Next Steps

With Flet installed and configured, you're ready to:

1. Learn about Flet's core concepts and architecture
2. Build your first Flet application
3. Explore controls and layouts
4. Deploy your app to different platforms

The next guide covers Flet's core concepts including controls, events, and state management.
