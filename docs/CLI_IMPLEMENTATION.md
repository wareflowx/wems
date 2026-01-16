# Phase 6: CLI Implementation Plan

**Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Planning
**Framework:** Typer
**Estimated Duration:** 1 week

---

## Table of Contents

1. [Overview](#overview)
2. [Why Typer?](#why-typer)
3. [Architecture](#architecture)
4. [Command Reference](#command-reference)
5. [Output Formatting](#output-formatting)
6. [Interactive Mode](#interactive-mode)
7. [Testing Strategy](#testing-strategy)
8. [Implementation Order](#implementation-order)
9. [Acceptance Criteria](#acceptance-criteria)
10. [Usage Examples](#usage-examples)

---

## Overview

### Objective

Create a command-line interface (CLI) to test all existing functionality before implementing the graphical UI. This CLI will provide temporary but complete access to all features of the application.

### Goals

- ✅ Test all existing modules (queries, calculations, export, utils, lock)
- ✅ Enable manual integration testing
- ✅ Validate business logic end-to-end
- ✅ Provide data import/export capabilities
- ✅ Facilitate rapid development and debugging

### Dependencies

All dependencies are already completed:
- ✅ Phase 1: Employee Module (queries, calculations)
- ✅ Phase 2: Lock Manager
- ✅ Phase 3: Utils Module (files, config, log)
- ✅ Phase 4: Excel Export

---

## Why Typer?

### Choice of Framework

**Selected:** [Typer](https://typer.tiangolo.com/) (instead of argparse or click)

### Advantages

| Feature | Benefit |
|---------|---------|
| **Type Hints Based** | Leverages Python type hints for automatic validation |
| **Less Boilerplate** | Minimal code compared to argparse/click |
| **Auto-Generated Help** | `--help` generated automatically from type hints |
| **Subcommands** | Native support for nested command groups |
| **Validation** | Automatic type conversion and validation |
| **Testable** | Can be imported as a module, easy to test |
| **Modern** | Actively maintained by FastAPI team |
| **Rich Output** | Optional integration with Rich library |

### Comparison

```python
# argparse (45+ lines)
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
add_parser = subparsers.add_parser('add')
add_parser.add_argument('--first-name', required=True)
add_parser.add_argument('--last-name', required=True)
# ... lots of boilerplate

# Typer (15 lines)
import typer
app = typer.Typer()

@app.command()
def add(first_name: str, last_name: str):
    """Add a new employee."""
    # Implementation
```

---

## Architecture

### File Structure

```
src/
├── cli.py                      # Main entry point with app()
├── cli/
│   ├── __init__.py
│   ├── employee.py             # Employee management commands
│   ├── caces.py                # CACES certification commands
│   ├── medical.py              # Medical visit commands
│   ├── training.py             # Online training commands
│   ├── report.py               # Reporting and export commands
│   ├── lock.py                 # Lock management commands
│   └── utils.py                # CLI utilities (formatting, colors)
```

### Main Application Structure

```python
# src/cli.py
import typer
from cli import employee, caces, medical, training, report, lock

# Main app
app = typer.Typer(
    name="employee-manager",
    help="Simple Employee Manager - Warehouse employee certification tracker",
    no_args_is_help=True,
    add_completion=True
)

# Register subcommands
app.add_typer(employee.app, name="employee", help="Employee management")
app.add_typer(caces.app, name="caces", help="CACES certification management")
app.add_typer(medical.app, name="medical", help="Medical visit management")
app.add_typer(training.app, name="training", help="Online training management")
app.add_typer(report.app, name="report", help="Reports and exports")
app.add_typer(lock.app, name="lock", help="Application lock management")

if __name__ == "__main__":
    app()
```

### Module Organization

Each module in `src/cli/` follows this pattern:

```python
# src/cli/employee.py
import typer
from employee.models import Employee
from employee import queries, calculations

app = typer.Typer(help="Employee management commands")

@app.app.command()
def list(
    active_only: bool = typer.Option(False, "--active", help="Show only active employees"),
    status: str = typer.Option(None, "--status", help="Filter by status"),
    role: str = typer.Option(None, "--role", help="Filter by role")
):
    """List all employees with optional filtering."""
    # Implementation

@app.app.command()
def show(employee_id: str):
    """Show detailed information for an employee."""
    # Implementation

# ... more commands
```

---

## Command Reference

### 1. Employee Commands

**Group:** `employee`

```bash
# List all employees
python -m cli employee list
python -m cli employee list --active
python -m cli employee list --status active --role Cariste

# Show employee details
python -m cli employee show <EMPLOYEE_ID>
python -m cli employee show WMS-001

# Add new employee (interactive)
python -m cli employee add

# Add new employee (non-interactive)
python -m cli employee add \
  --first-name "Jean" \
  --last-name "Dupont" \
  --external-id "WMS-001" \
  --workspace "Quai" \
  --role "Cariste" \
  --contract "CDI" \
  --entry-date "2020-01-15"

# Update employee
python -m cli employee update WMS-001 \
  --workspace "Zone A" \
  --role "Magasinier"

# Delete employee (with confirmation)
python -m cli employee delete WMS-001

# Show compliance score
python -m cli employee compliance WMS-001
```

#### Command Details

| Command | Arguments | Options | Description |
|---------|-----------|---------|-------------|
| `list` | None | `--active`, `--status`, `--role`, `--workspace` | List employees with filters |
| `show` | `employee_id` | None | Display detailed employee info |
| `add` | None | All employee fields as options | Create new employee |
| `update` | `employee_id` | Fields to update | Update employee data |
| `delete` | `employee_id | `--yes` (skip confirmation) | Delete employee |
| `compliance` | `employee_id` | None | Show compliance score and status |

---

### 2. CACES Commands

**Group:** `caces`

```bash
# List all CACES for an employee
python -m cli caces list WMS-001

# Add CACES certification
python -m cli caces add WMS-001 \
  --kind "R489-1A" \
  --completion-date "2020-03-01" \
  --document "/path/to/caces.pdf"

# Update CACES
python -m cli caces update <CACES_ID> \
  --kind "R489-2B" \
  --completion-date "2021-06-15"

# Delete CACES
python -m cli caces delete <CACES_ID>

# Show expiring CACES
python -m cli caces expiring --days 30

# Show expired CACES
python -m cli caces expired
```

#### CACES Types

Valid `--kind` values:
- `R489-1A` - Catégorie 1A
- `R489-1B` - Catégorie 1B
- `R489-2` - Catégorie 2
- `R489-3` - Catégorie 3
- `R489-4` - Catégorie 4
- `R489-5` - Catégorie 5

---

### 3. Medical Visit Commands

**Group:** `medical`

```bash
# List medical visits for an employee
python -m cli medical list WMS-001

# Add medical visit
python -m cli medical add WMS-001 \
  --type "periodic" \
  --date "2024-01-15" \
  --result "fit" \
  --document "/path/to/visit.pdf"

# Update medical visit
python -m cli medical update <VISIT_ID> \
  --result "fit_with_restrictions"

# Delete medical visit
python -m cli medical delete <VISIT_ID>

# Show expiring visits
python -m cli medical expiring --days 30

# Show unfit employees
python -m cli medical unfit
```

#### Visit Types

Valid `--type` values:
- `initial` - Initial hiring visit
- `periodic` - Periodic examination
- `recovery` - Return to work visit

#### Visit Results

Valid `--result` values:
- `fit` - Fit for work
- `unfit` - Unfit for work
- `fit_with_restrictions` - Fit with work restrictions

---

### 4. Training Commands

**Group:** `training`

```bash
# List trainings for an employee
python -m cli training list WMS-001

# Add training with expiration
python -m cli training add WMS-001 \
  --title "Safety Training" \
  --completion-date "2024-01-15" \
  --validity-months 12 \
  --certificate "/path/to/cert.pdf"

# Add permanent training
python -m cli training add WMS-001 \
  --title "Fire Safety" \
  --completion-date "2024-01-15" \
  --permanent

# Update training
python -m cli training update <TRAINING_ID> \
  --title "Updated Title"

# Delete training
python -m cli training delete <TRAINING_ID>

# Show expiring trainings
python -m cli training expiring --days 30
```

---

### 5. Report Commands

**Group:** `report`

```bash
# Display dashboard
python -m cli report dashboard

# Show alerts
python -m cli report alerts --critical-days 7 --warning-days 30

# Export to Excel
python -m cli report export output.xlsx
python -m cli report export output.xlsx --include-caces --no-visits

# Show global statistics
python -m cli report stats

# Show unfit employees
python -m cli report unfit

# Show compliance summary
python -m cli report compliance
```

#### Export Options

| Option | Description | Default |
|--------|-------------|---------|
| `--include-caces` | Include CACES sheet | True |
| `--include-visits` | Include medical visits sheet | True |
| `--include-trainings` | Include trainings sheet | True |
| `--no-caces` | Exclude CACES sheet | False |
| `--no-visits` | Exclude visits sheet | False |
| `--no-trainings` | Exclude trainings sheet | False |

---

### 6. Lock Commands

**Group:** `lock`

```bash
# Show lock status
python -m cli lock status

# Acquire lock manually
python -m cli lock acquire

# Release lock manually
python -m cli lock release

# Refresh heartbeat manually
python -m cli lock refresh

# Show lock information
python -m cli lock info
```

---

## Output Formatting

### Table Format with `tabulate`

```python
from tabulate import tabulate

def format_employee_table(employees):
    """Format employees as a table."""
    headers = ["ID WMS", "Nom", "Zone", "Poste", "Contrat", "Statut", "Compliance"]
    rows = []

    for emp in employees:
        compliance_status = get_compliance_status(emp)
        emoji = get_compliance_emoji(compliance_status)

        rows.append([
            emp.external_id,
            emp.full_name,
            emp.workspace,
            emp.role,
            emp.contract_type,
            "Actif" if emp.is_active else "Inactif",
            f"{emoji} {compliance_status.capitalize()}"
        ])

    return tabulate(rows, headers=headers, tablefmt="grid")
```

### Output Example

```
┌─────────┬───────────────┬────────┬──────────┬──────────┬────────┬─────────────┐
│ ID WMS  │ Nom           │ Zone   │ Poste    │ Contrat  │ Statut │ Compliance  │
├─────────┼───────────────┼────────┼──────────┼──────────┼────────┼─────────────┤
│ WMS-001 │ Jean Dupont   │ Quai   │ Cariste  │ CDI      │ Actif  │ 🟢 Conforme │
│ WMS-002 │ Marie Martin  │ Zone A │ Prép.    │ CDD      │ Actif  │ 🟠 Attention │
│ WMS-003 │ Pierre Bernard│ Bureau │ Magasin. │ CDI      │ Inactif│ ⚪ Inconnu   │
└─────────┴───────────────┴────────┴──────────┴──────────┴────────┴─────────────┘
```

### Compliance Emoji Mapping

| Status | Emoji | Description |
|--------|-------|-------------|
| `compliant` | 🟢 | All items valid |
| `warning` | 🟠 | Items expiring within 30 days |
| `critical` | 🔴 | Expired items present |
| `unknown` | ⚪ | No compliance items |

### Rich Output with `rich` (Optional)

```python
from rich.console import Console
from rich.table import Table as RichTable

console = Console()

def print_rich_dashboard(data):
    """Print dashboard with rich formatting."""
    table = RichTable(title="📊 Tableau de Bord", show_header=True, header_style="bold magenta")
    table.add_column("Métrique", style="cyan", width=30)
    table.add_column("Valeur", style="green", width=15)

    table.add_row("Employés actifs", str(data['active_employees']))
    table.add_row("Employés total", str(data['total_employees']))
    table.add_row("CACES expirés", f"[red]{data['expired_caces']}[/red]")
    table.add_row("Visites expirées", f"[red]{data['expired_visits']}[/red]")

    console.print(table)
```

---

## Interactive Mode

### Prompt Library: `questionary`

```python
import questionary
from datetime import datetime

def prompt_employee_data():
    """Interactive prompt for employee creation."""
    first_name = questionary.text("Prénom:").ask()
    last_name = questionary.text("Nom:").ask()
    external_id = questionary.text("ID WMS:").ask()

    workspace = questionary.select(
        "Zone:",
        choices=["Quai", "Zone A", "Zone B", "Bureau"]
    ).ask()

    role = questionary.select(
        "Poste:",
        choices=["Cariste", "Préparateur", "Magasinier"]
    ).ask()

    contract_type = questionary.select(
        "Type de contrat:",
        choices=["CDI", "CDD", "Intérim"]
    ).ask()

    entry_date_str = questionary.text(
        "Date d'entrée (YYYY-MM-DD):",
        validate=lambda x: len(x) == 10
    ).ask()

    entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()

    return {
        'first_name': first_name,
        'last_name': last_name,
        'external_id': external_id,
        'workspace': workspace,
        'role': role,
        'contract_type': contract_type,
        'entry_date': entry_date
    }
```

### Interactive Session Example

```bash
$ python -m cli employee add
? Prénom: Jean
? Nom: Dupont
? ID WMS: WMS-001
? Zone: [Quai, Zone A, Zone B, Bureau]
  Quai
? Poste: [Cariste, Préparateur, Magasinier]
  Cariste
? Type de contrat: [CDI, CDD, Intérim]
  CDI
? Date d'entrée (YYYY-MM-DD): 2020-01-15

✅ Employé créé avec succès
   ID: WMS-001
   Nom: Jean Dupont
   Statut: Actif
```

### Confirmation Prompts

```python
def confirm_delete(employee_id: str, force: bool = False) -> bool:
    """Confirm employee deletion."""
    if force:
        return True

    employee = Employee.get_or_none(Employee.external_id == employee_id)
    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    typer.echo(f"🗑️  Supprimer l'employé: {employee.full_name} ({employee_id})")
    confirm = questionary.confirm("Êtes-vous sûr?", default=False).ask()

    if not confirm:
        typer.echo("❌ Suppression annulée")
        raise typer.Exit(0)

    return True
```

---

## Testing Strategy

### Typer Testing with `CliRunner`

```python
from typer.testing import CliRunner
from cli import app

runner = CliRunner()

def test_add_employee():
    """Test adding employee via CLI."""
    result = runner.invoke(app, [
        "employee", "add",
        "--first-name", "Jean",
        "--last-name", "Dupont",
        "--external-id", "WMS-TEST",
        "--workspace", "Quai",
        "--role", "Cariste",
        "--contract", "CDI",
        "--entry-date", "2020-01-15"
    ])

    assert result.exit_code == 0
    assert "Jean Dupont" in result.stdout
    assert "WMS-TEST" in result.stdout
    assert "créé avec succès" in result.stdout.lower()

def test_list_employees(db, sample_employee):
    """Test listing employees."""
    result = runner.invoke(app, ["employee", "list"])

    assert result.exit_code == 0
    assert sample_employee.external_id in result.stdout
    assert sample_employee.full_name in result.stdout

def test_show_employee(db, sample_employee):
    """Test showing employee details."""
    result = runner.invoke(app, ["employee", "show", sample_employee.external_id])

    assert result.exit_code == 0
    assert sample_employee.full_name in result.stdout
    assert sample_employee.workspace in result.stdout

def test_export_excel(db, sample_employee, tmp_path):
    """Test Excel export."""
    output = tmp_path / "test_export.xlsx"
    result = runner.invoke(app, ["report", "export", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Export terminé" in result.stdout

def test_non_existent_employee():
    """Test error handling for non-existent employee."""
    result = runner.invoke(app, ["employee", "show", "NONEXISTENT"])

    assert result.exit_code != 0
    assert "non trouvé" in result.stdout.lower() or "not found" in result.stdout.lower()
```

### Integration Tests

```python
def test_full_workflow_cli(db, tmp_path):
    """Test complete workflow via CLI."""
    # 1. Create employee
    result = runner.invoke(app, [
        "employee", "add",
        "--first-name", "Test",
        "--last-name", "User",
        "--external-id", "CLI-001",
        "--workspace", "Quai",
        "--role", "Cariste",
        "--contract", "CDI",
        "--entry-date", "2020-01-15"
    ])
    assert result.exit_code == 0

    # 2. Add CACES
    result = runner.invoke(app, [
        "caces", "add", "CLI-001",
        "--kind", "R489-1A",
        "--completion-date", "2020-03-01"
    ])
    assert result.exit_code == 0

    # 3. Check compliance
    result = runner.invoke(app, ["employee", "compliance", "CLI-001"])
    assert result.exit_code == 0
    assert "95" in result.stdout or "100" in result.stdout

    # 4. Add medical visit
    result = runner.invoke(app, [
        "medical", "add", "CLI-001",
        "--type", "periodic",
        "--date", "2024-01-15",
        "--result", "fit"
    ])
    assert result.exit_code == 0

    # 5. Export to Excel
    output = tmp_path / "export.xlsx"
    result = runner.invoke(app, ["report", "export", str(output)])
    assert result.exit_code == 0
    assert output.exists()

    # 6. Delete employee
    result = runner.invoke(app, ["employee", "delete", "CLI-001", "--yes"])
    assert result.exit_code == 0
```

### Test Coverage Requirements

- ✅ Each command has unit tests
- ✅ Each command group has integration tests
- ✅ Input validation tested
- ✅ Error handling tested
- ✅ Full workflow scenarios tested
- ✅ Target: >80% code coverage

---

## Implementation Order

### Phase 6.1: Infrastructure (Day 1)

**Tasks:**
- [ ] Create `src/cli.py` main entry point
- [ ] Create `src/cli/` directory structure
- [ ] Add dependencies to `pyproject.toml`
- [ ] Test basic CLI: `python -m cli --help`
- [ ] Test completion: `python -m cli --install-completion`

**Dependencies to Add:**
```toml
[project.dependencies]
typer = {extras = ["all"], version = "^0.12.0"}
rich = "^13.7.0"
tabulate = "^0.9.0"
questionary = "^2.0.0"
```

**Acceptance:**
```bash
$ python -m cli --help
 Usage: employee-manager [OPTIONS] COMMAND [ARGS]...

   Simple Employee Manager - Warehouse employee certification tracker

╭─ Commands ────────────────────────────────────────────────────────────╮
│ employee   Employee management                                        │
│ caces      CACES certification management                             │
│ medical    Medical visit management                                   │
│ training   Online training management                                 │
│ report     Reports and exports                                        │
│ lock       Application lock management                                │
╰────────────────────────────────────────────────────────────────────────╯
```

---

### Phase 6.2: Employee Commands (Days 2-3)

**Priority:** CRITICAL

**Tasks:**
- [ ] `employee list` with filtering
- [ ] `employee show` with detailed output
- [ ] `employee add` (interactive + flags)
- [ ] `employee update` with partial updates
- [ ] `employee delete` with confirmation
- [ ] `employee compliance` with score display
- [ ] Unit tests for all commands
- [ ] Integration tests for employee workflows

**Acceptance:**
```bash
$ python -m cli employee list
┌─────────┬───────────────┬────────┬──────────┐
│ ID WMS  │ Nom           │ Zone   │ Poste    │
├─────────┼───────────────┼────────┼──────────┤
│ WMS-001 │ Jean Dupont   │ Quai   │ Cariste  │
└─────────┴───────────────┴────────┴──────────┘

$ python -m cli employee show WMS-001
ID WMS:        WMS-001
Nom:           Jean Dupont
Zone:          Quai
Poste:         Cariste
Contrat:       CDI
Date entrée:   2020-01-15
Statut:        Actif
Compliance:    🟢 Conforme (95/100)
```

---

### Phase 6.3: Report Commands (Days 3-4)

**Priority:** CRITICAL

**Tasks:**
- [ ] `report dashboard` with statistics table
- [ ] `report alerts` with color-coded output
- [ ] `report export` calling existing export module
- [ ] `report stats` with global metrics
- [ ] `report unfit` listing unfit employees
- [ ] Unit tests for all commands
- [ ] Integration tests with real data

**Acceptance:**
```bash
$ python -m cli report dashboard
┌────────────────────────────────────────────┐
│         📊 Tableau de Bord                 │
├────────────────────────────────────────────┤
│ Employés actifs:        42                  │
│ Employés total:         45                  │
│ CACES expirés:          2                   │
│ CACES critiques (<30j): 5                   │
│ Visites expirées:       1                   │
│ Employés inaptes:       1                   │
└────────────────────────────────────────────┘

$ python -m cli report alerts
🔔 ALERTES - Items expirant dans les 30 prochains jours

🔴 CRITIQUES (< 7 jours)
  ├─ WMS-005: CACES R489-2B expire dans 5 jours
  └─ WMS-012: Visite médicale expirée depuis 2 jours

🟠 ATTENTION (< 30 jours)
  ├─ WMS-003: Formation "Safety" expire dans 22 jours
  └─ WMS-008: Visite médicale expire dans 18 jours
```

---

### Phase 6.4: CACES, Medical, Training Commands (Days 4-5)

**Priority:** MEDIUM

**Tasks:**
- [ ] CACES CRUD commands
- [ ] Medical visit CRUD commands
- [ ] Training CRUD commands
- [ ] Expiration queries for each type
- [ ] Unit tests for each command group
- [ ] Integration tests

**Acceptance:**
```bash
$ python -m cli caces list WMS-001
┌──────┬──────────┬───────────────┬─────────────┬──────────────┐
│ Type │ Obtention│ Expiration    │ Jours rest. │ Statut       │
├──────┼──────────┼───────────────┼─────────────┼──────────────┤
│R489-1A│2020-03-01│ 2030-03-01   │ 1450        │ 🟢 Valide    │
└──────┴──────────┴───────────────┴─────────────┴──────────────┘
```

---

### Phase 6.5: Lock Commands (Day 5)

**Priority:** MEDIUM

**Tasks:**
- [ ] `lock status` display current lock
- [ ] `lock acquire` manual acquisition
- [ ] `lock release` manual release
- [ ] `lock refresh` manual heartbeat
- [ ] `lock info` detailed lock information
- [ ] Unit tests

**Acceptance:**
```bash
$ python -m cli lock status
🔒 Verrou applicatif
  Statut:    Actif
  Propriétaire: PC-01 (alice)
  PID:       12345
  Acquis:    2024-01-15 10:30:00
  Heartbeat: 2024-01-15 11:45:23 (il y a 15 secondes)

$ python -m cli lock acquire
✅ Verrou acquis avec succès
  Hostname: PC-01
  PID: 12345
```

---

### Phase 6.6: Interactive Mode & Polish (Day 6-7)

**Priority:** MEDIUM

**Tasks:**
- [ ] Implement `questionary` for all add commands
- [ ] Add confirmation prompts for delete operations
- [ ] Add progress indicators for long operations
- [ ] Implement `rich` output formatting (optional)
- [ ] Add colors and emojis to output
- [ ] Improve error messages
- [ ] Add comprehensive `--help` text
- [ ] Final integration tests
- [ ] Documentation

**Acceptance:**
- All commands work in both interactive and non-interactive modes
- Clear, colored output with emojis
- Helpful error messages
- Comprehensive help text
- All tests passing

---

## Acceptance Criteria

### Functionality

- [ ] All 6 command groups implemented (employee, caces, medical, training, report, lock)
- [ ] ~30 total commands implemented
- [ ] Interactive mode working with `questionary`
- [ ] Non-interactive mode with flags
- [ ] Tabular output formatting with `tabulate`
- [ ] Auto-generated help messages (Typer)
- [ ] Error handling with clear messages

### Testing

- [ ] Unit tests for each command (>30 tests)
- [ ] Integration tests for workflows (>10 tests)
- [ ] Input validation tests
- [ ] Error handling tests
- [ ] Test coverage >80%

### Documentation

- [ ] `--help` works for all commands
- [ ] Usage examples in docstrings
- [ ] Clear error messages
- [ ] This implementation document complete

### Quality

- [ ] Code organized in logical modules
- [ ] Complete type hints (required by Typer)
- [ ] Automatic type validation
- [ ] Clean, readable code
- [ ] No code duplication

---

## Usage Examples

### Example 1: Complete Employee Workflow

```bash
# 1. Create a new employee
$ python -m cli employee add
? Prénom: Jean
? Nom: Dupont
? ID WMS: WMS-001
? Zone: Quai
? Poste: Cariste
? Type de contrat: CDI
? Date d'entrée (YYYY-MM-DD): 2020-01-15

✅ Employé créé avec succès
   ID: WMS-001
   Nom: Jean Dupont
   Statut: Actif

# 2. Add CACES certification
$ python -m cli caces add WMS-001 \
  --kind "R489-1A" \
  --completion-date "2020-03-01"

✅ CACES ajouté: R489-1A
   Employé: Jean Dupont (WMS-001)
   Expiration: 2030-03-01

# 3. Add medical visit
$ python -m cli medical add WMS-001 \
  --type "periodic" \
  --date "2024-01-15" \
  --result "fit"

✅ Visite médicale ajoutée
   Employé: Jean Dupont (WMS-001)
   Résultat: Fit

# 4. Check compliance status
$ python -m cli employee compliance WMS-001
┌────────────────────────────────────────┐
│  Compliance: Jean Dupont (WMS-001)     │
├────────────────────────────────────────┤
│  Score:        100/100                  │
│  Statut:       🟢 Conforme              │
│  CACES:        1 valide                 │
│  Visites:      1 valide                 │
│  Formations:   0                        │
│  Actions req.: Aucune                   │
└────────────────────────────────────────┘

# 5. Export to Excel
$ python -m cli report export employes_2024.xlsx --include-caces --include-visits
✅ Export terminé: employes_2024.xlsx
   Feuilles: Résumé, Employés, CACES, Visites Médicales
   Durée: 0.45 secondes
```

---

### Example 2: Checking Alerts

```bash
$ python -m cli report alerts --critical-days 7 --warning-days 30
┌─────────────────────────────────────────────────────────┐
│  🔔 ALERTES - Items expirant dans les 30 prochains jours│
├─────────────────────────────────────────────────────────┤
│  🔴 CRITIQUES (< 7 jours)                              │
│  ├─ WMS-005: CACES R489-2B expire dans 5 jours         │
│  │   ├─ Employé: Marie Martin                          │
│  │   └─ Poste: Préparateur de commandes               │
│  ├─ WMS-012: Visite médicale expirée depuis 2 jours    │
│  │   ├─ Employé: Pierre Bernard                        │
│  │   └─ Poste: Magasinier                             │
│  └─ WMS-018: Formation "Safety" expirée depuis 12h     │
│      ├─ Employé: Sophie Petit                          │
│      └─ Poste: Cariste                                 │
├─────────────────────────────────────────────────────────┤
│  🟠 ATTENTION (< 30 jours)                             │
│  ├─ WMS-003: Formation "Safety" expire dans 22 jours   │
│  │   ├─ Employé: Jean Dupont                           │
│  │   └─ Poste: Cariste                                 │
│  ├─ WMS-008: Visite médicale expire dans 18 jours      │
│  │   ├─ Employé: Anne Laurent                          │
│  │   └─ Poste: Préparateur                            │
│  └─ WMS-015: CACES R489-3 expire dans 25 jours         │
│      ├─ Employé: Luc Moreau                            │
│      └─ Poste: Cariste                                 │
└─────────────────────────────────────────────────────────┘

Total: 3 critiques, 3 attentions
```

---

### Example 3: Dashboard and Statistics

```bash
$ python -m cli report dashboard
┌──────────────────────────────────────────────────────┐
│            📊 Tableau de Bord                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📈 Effectif                                         │
│  ├─ Employés total:        45                        │
│  ├─ Employés actifs:       42                        │
│  └─ Employés inactifs:     3                         │
│                                                      │
│  🚨 Conformité                                       │
│  ├─ 🟢 Conformes:          38 (89%)                  │
│  ├─ 🟠 Attention:           3 (7%)                    │
│  └─ 🔴 Critiques:           2 (4%)                    │
│                                                      │
│  📜 Certifications                                  │
│  ├─ CACES totaux:          87                        │
│  ├─ CACES expirés:         2                         │
│  ├─ CACES critiques:       5                         │
│  └─ Visites expirées:      1                         │
│                                                      │
│  👷 Postes                                           │
│  ├─ Caristes:              22                        │
│  ├─ Préparateurs:          15                        │
│  └─ Magasiniers:           8                         │
│                                                      │
└──────────────────────────────────────────────────────┘

Dernière mise à jour: 2024-01-15 14:30:00
```

---

### Example 4: Lock Management

```bash
# Check current lock status
$ python -m cli lock status
🔒 État du verrou applicatif

  Statut:    🔒 Verrouillé
  Propriétaire:
    Hostname: PC-01
    User:     alice
    PID:      12345

  Temps:
    Acquis:       2024-01-15 10:30:00
    Heartbeat:    2024-01-15 14:45:23
    Âge:          4 heures 15 minutes

# Manually acquire lock
$ python -m cli lock acquire
✅ Verrou acquis avec succès

  Détails:
    Hostname: PC-01
    Username: alice
    PID:      12345
    Acquis:   2024-01-15 14:50:00

# Refresh heartbeat manually
$ python -m cli lock refresh
✅ Heartbeat rafraîchi: 2024-01-15 14:52:00

# Release lock
$ python -m cli lock release
? Confirmer la libération du verrou? [y/N]: y
✅ Verrou libéré avec succès
```

---

## Dependencies

### Required Packages

```toml
[project.dependencies]
typer = {extras = ["all"], version = "^0.12.0"}
rich = "^13.7.0"
tabulate = "^0.9.0"
questionary = "^2.0.0"
```

### Installation

```bash
# Install all CLI dependencies
uv add typer rich tabulate questionary

# Or with pip
pip install "typer[all]" rich tabulate questionary
```

### Package Breakdown

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| typer | ^0.12.0 | CLI framework with type hints | Yes |
| rich | ^13.7.0 | Rich terminal output | Recommended |
| tabulate | ^0.9.0 | Table formatting | Yes |
| questionary | ^2.0.0 | Interactive prompts | Recommended |

---

## Success Metrics

### Completion Criteria

- [ ] All 6 command groups implemented
- [ ] All ~30 commands working
- [ ] Interactive mode functional
- [ ] Non-interactive mode with all flags
- [ ] Test coverage >80%
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Help messages auto-generated

### Performance Targets

| Metric | Target |
|--------|--------|
| Command startup time | <100ms |
| List command (1000 employees) | <500ms |
| Export command (100 employees) | <5s |
| Dashboard command | <200ms |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Code coverage | >80% |
| Type hint coverage | 100% (required by Typer) |
| Pylint score | >8.0 |
| Mypy type checking | Pass |

---

## Next Steps

### Implementation Sequence

1. ✅ **Day 1:** Infrastructure and basic setup
2. ✅ **Days 2-3:** Employee commands (priority)
3. ✅ **Days 3-4:** Report commands (priority)
4. ✅ **Days 4-5:** CACES, Medical, Training commands
5. ✅ **Day 5:** Lock commands
6. ✅ **Days 6-7:** Interactive mode, polish, documentation

### Post-Implementation

After CLI completion:
- Manual testing of all workflows
- Performance testing with large datasets
- Bug fixes and refinements
- **Phase 5:** Validators (optional, can be done after CLI)
- **Phase 7:** Flet UI (final phase)

---

## Appendix

### A. Command Quick Reference

| Group | Commands | Count |
|-------|----------|-------|
| `employee` | list, show, add, update, delete, compliance | 6 |
| `caces` | list, add, update, delete, expiring, expired | 6 |
| `medical` | list, add, update, delete, expiring, unfit | 6 |
| `training` | list, add, update, delete, expiring | 5 |
| `report` | dashboard, alerts, export, stats, unfit, compliance | 6 |
| `lock` | status, acquire, release, refresh, info | 5 |
| **Total** | | **34** |

### B. Type Hints Reference

```python
# Common type hints for CLI commands
from pathlib import Path
from datetime import date
from typing import Optional

def example_command(
    # String with choice validation
    role: str = typer.Option(..., "--role", help="Employee role"),

    # Date with automatic parsing
    entry_date: date = typer.Option(..., "--entry-date", help="Entry date"),

    # Path with validation
    document: Path = typer.Option(None, "--document", help="Document path"),

    # Integer with range
    validity_months: Optional[int] = typer.Option(None, "--validity-months", min=1, max=120),

    # Boolean flag
    active_only: bool = typer.Option(False, "--active", help="Active only"),

    # Enum-like choices
    visit_type: str = typer.Option(..., "--type", help="Visit type", click_type=click.Choice(['initial', 'periodic', 'recovery']))
):
    pass
```

### C. Error Handling Pattern

```python
def safe_cli_command():
    """Pattern for safe CLI execution."""
    try:
        # Command logic here
        result = perform_operation()
        typer.echo(f"✅ Success: {result}")
    except FileNotFoundError as e:
        typer.echo(f"❌ File not found: {e}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"❌ Invalid value: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)
```

---

**Document Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Ready for Implementation
**Next Phase:** Phase 7 - Flet UI (after CLI completion)
