<<<<<<< HEAD
404: Not Found
=======
# GitHub Actions CI/CD

This repository uses GitHub Actions for continuous integration and code quality checks.

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to any branch
- Pull requests
- Manual workflow dispatch

**Jobs:**

#### Quality
- Runs Ruff linter with `ruff check .`
- Checks code formatting with `ruff format --check .`
- Fails if linting errors are found

#### Tests
- Runs pytest with coverage reporting
- Excludes UI tests (`tests/test_ui`)
- Uploads coverage to Codecov (optional)

### 2. PR Checks (`.github/workflows/pr-checks.yml`)

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**

#### Changes
- Detects which files changed (src vs tests)

#### Full Test Suite
- Runs if source or test files changed
- Executes full test suite excluding UI tests

#### Size Check
- Warns if PR is larger than 500 lines
- Uses `lets-maybe/fix-pr-size` action

## Local Development

### Install Dev Tools

```bash
uv sync --dev
```

### Run Linter

```bash
# Check code
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Check formatting
uv run ruff format --check .

# Format code
uv run ruff format .
```

### Run Tests

```bash
# Run all tests (excluding UI)
uv run pytest --ignore=tests/test_ui

# Run specific test file
uv run pytest tests/test_app.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

### Before Committing

```bash
# 1. Format code
uv run ruff format .

# 2. Check linting
uv run ruff check .

# 3. Run tests
uv run pytest --ignore=tests/test_ui

# 4. Commit
git add .
git commit -m "feat: your changes"
```

## Code Quality Standards

### Ruff Configuration (`pyproject.toml`)

- **Line length**: 120 characters
- **Python version**: 3.14
- **Enabled rules**:
  - `E`: pycodestyle errors
  - `W`: pycodestyle warnings
  - `F`: pyflakes
  - `I`: isort (import sorting)

### Per-File Ignores

- **Scripts** (`scripts/*.py`): F401, F841, E722, F541
  - Allow unused imports, unused variables, bare except, f-string issues
- **CLI code** (`src/cli/*.py`): B008, B904, UP045, F401, F841, F541, C416
  - Allow function calls in defaults, typer patterns, etc.

### Coverage Requirements

- **Minimum coverage**: 70%
- **Measured on**: `src/` directory
- **Excludes**: Tests, `__pycache__`

## Branch Protection

To enable CI checks as required for merging:

1. Go to **Settings** > **Branches**
2. Add/Edit rule for `main` branch
3. Enable **Require status checks to pass before merging**
4. Select required checks:
   - `Code Quality`
   - `Tests`
   - `Full Test Suite` (for PRs)

## Troubleshooting

### CI fails but local tests pass

```bash
# Ensure dependencies are up to date
uv sync --dev

# Run exact same command as CI
uv run pytest --cov=src --cov-report=xml --ignore=tests/test_ui
```

### Ruff errors

```bash
# Auto-fix most issues
uv run ruff check . --fix

# Format imports
uv run ruff check . --select I --fix
```

### Coverage failures

```bash
# Generate detailed report
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Open HTML report to see what's not covered
open htmlcov/index.html
```

## Future Improvements

- [ ] Add type checking with mypy
- [ ] Add security scanning with bandit
- [ ] Add dependency checking with dependabot
- [ ] Add performance benchmarking
- [ ] Add code complexity reports
- [ ] Enable strict mode for Ruff (B, UP rules)
- [ ] Add pre-commit hooks
>>>>>>> origin/main
