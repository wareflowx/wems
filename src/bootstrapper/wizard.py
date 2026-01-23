"""Setup wizard for initial Wareflow EMS configuration.

This module provides an interactive command-line wizard that guides
users through the initial configuration process, making it easy to
set up Wareflow EMS without manual file editing.

Example:
    >>> from bootstrapper.wizard import run_setup_wizard
    >>> run_setup_wizard()
"""

from pathlib import Path
from typing import Any, Dict, List

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from utils import config

console = Console()


# Default values and suggestions
DEFAULT_WORKSPACES = ["Quai", "Zone A", "Zone B", "Zone C", "Bureau", "Stockage"]
DEFAULT_ROLES = [
    "Cariste",
    "Préparateur de commandes",
    "Magasinier",
    "Réceptionnaire",
    "Gestionnaire",
    "Chef d'équipe",
]
DEFAULT_CONTRACT_TYPES = ["CDI", "CDD", "Intérim", "Alternance", "Stage"]


def print_header() -> None:
    """Print the wizard header."""
    header_text = Text()
    header_text.append("Wareflow EMS Configuration Wizard\n", style="bold cyan")
    header_text.append("====================================\n\n", style="bold cyan")
    header_text.append(
        "This wizard will help you configure Wareflow EMS for your company.\n",
        style="default",
    )
    header_text.append(
        "You'll be asked a few questions to set up the basic configuration.\n",
        style="dim",
    )

    panel = Panel(
        header_text,
        title="[bold blue]Welcome[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def print_step(step_num: int, total_steps: int, title: str) -> None:
    """Print a step header.

    Args:
        step_num: Current step number
        total_steps: Total number of steps
        title: Step title
    """
    console.print(f"\n[bold cyan] Step {step_num}/{total_steps}[/bold cyan] [bold white]{title}[/bold white]")
    console.print("[dim]" + "─" * 60 + "[/dim]\n")


def ask_company_info() -> Dict[str, str]:
    """Ask for company information.

    Returns:
        Dictionary with company_name, contact_email, contact_phone
    """
    print_step(1, 7, "Company Information")

    company_name = questionary.text(
        "Company name:",
        default="My Warehouse",
        instruction="e.g., Mon Entrepôt SARL",
    ).ask()

    contact_email = questionary.text(
        "Contact email:",
        default="",
        instruction="Optional - for notifications and updates",
    ).ask()

    contact_phone = questionary.text(
        "Phone:",
        default="",
        instruction="Optional",
    ).ask()

    return {
        "company_name": company_name or "My Warehouse",
        "contact_email": contact_email or "",
        "contact_phone": contact_phone or "",
    }


def ask_organization() -> Dict[str, List[str]]:
    """Ask for organization structure.

    Returns:
        Dictionary with workspaces and roles lists
    """
    print_step(2, 7, "Organization Setup")

    # Ask for workspaces
    console.print("[dim]💡 Common workspaces: Quai, Zone A, Zone B, Bureau, Réception, Expédition[/dim]\n")

    use_default_workspaces = questionary.confirm(
        "Use default workspaces?",
        default=True,
        instruction=f"Defaults: {', '.join(DEFAULT_WORKSPACES[:3])}...",
    ).ask()

    if use_default_workspaces:
        workspaces = DEFAULT_WORKSPACES
    else:
        workspaces_input = questionary.text(
            "Workspaces (comma-separated):",
            default="Quai, Zone A, Zone B, Bureau",
            instruction="Separate with commas",
        ).ask()
        workspaces = [w.strip() for w in workspaces_input.split(",") if w.strip()]

    # Ask for roles
    console.print(f"\n[dim]💡 Common roles: {', '.join(DEFAULT_ROLES[:4])}...[/dim]\n")

    use_default_roles = questionary.confirm(
        "Use default roles?",
        default=True,
        instruction=f"Defaults: {', '.join(DEFAULT_ROLES[:3])}...",
    ).ask()

    if use_default_roles:
        roles = DEFAULT_ROLES
    else:
        roles_input = questionary.text(
            "Roles (comma-separated):",
            default="Cariste, Magasinier, Préparateur",
            instruction="Separate with commas",
        ).ask()
        roles = [r.strip() for r in roles_input.split(",") if r.strip()]

    return {
        "workspaces": workspaces,
        "roles": roles,
    }


def ask_alerts() -> Dict[str, int]:
    """Ask for alert configuration.

    Returns:
        Dictionary with critical_days, warning_days, info_days
    """
    print_step(3, 7, "Alert Configuration")

    console.print("[dim]Alert when CACES/medical visits are about to expire[/dim]\n")

    critical_days = questionary.text(
        "Critical alert threshold (days):",
        default="7",
        instruction="Alert when expiring within this many days",
        validate=lambda x: x.isdigit() and int(x) > 0,
    ).ask()

    warning_days = questionary.text(
        "Warning alert threshold (days):",
        default="30",
        instruction="Warning when expiring within this many days",
        validate=lambda x: x.isdigit() and int(x) > int(critical_days),
    ).ask()

    info_days = questionary.text(
        "Info alert threshold (days):",
        default="90",
        instruction="Info when expiring within this many days",
        validate=lambda x: x.isdigit() and int(x) > int(warning_days),
    ).ask()

    return {
        "critical_days": int(critical_days),
        "warning_days": int(warning_days),
        "info_days": int(info_days),
    }


def ask_database() -> Dict[str, Any]:
    """Ask for database configuration.

    Returns:
        Dictionary with database settings
    """
    print_step(4, 7, "Database Configuration")

    db_filename = questionary.text(
        "Database filename:",
        default="employee_manager.db",
        instruction="Name of the SQLite database file",
    ).ask()

    backup_retention = questionary.text(
        "Backup retention (days):",
        default="30",
        instruction="How long to keep backup files",
        validate=lambda x: x.isdigit() and int(x) >= 0,
    ).ask()

    enable_auto_backup = questionary.confirm(
        "Enable automatic backups?",
        default=True,
        instruction="Back up database daily",
    ).ask()

    return {
        "database_filename": db_filename or "employee_manager.db",
        "backup_retention": int(backup_retention),
        "enable_auto_backup": enable_auto_backup,
    }


def ask_interface() -> Dict[str, str]:
    """Ask for interface customization.

    Returns:
        Dictionary with interface settings
    """
    print_step(5, 7, "Interface Customization")

    app_title = questionary.text(
        "Window title:",
        default="Wareflow EMS",
        instruction="Application window title",
    ).ask()

    theme = questionary.select(
        "Theme:",
        choices=[
            questionary.Choice("System", value="system"),
            questionary.Choice("Light", value="light"),
            questionary.Choice("Dark", value="dark"),
        ],
        default="System",
    ).ask()

    return {
        "app_title": app_title or "Wareflow EMS",
        "theme": theme,
    }


def ask_advanced() -> Dict[str, bool]:
    """Ask for advanced features.

    Returns:
        Dictionary with advanced feature flags
    """
    print_step(6, 7, "Advanced Features")

    enable_audit = questionary.confirm(
        "Enable audit trail?",
        default=False,
        instruction="Track all changes to employee records",
    ).ask()

    return {
        "enable_audit": enable_audit,
    }


def print_summary(answers: Dict[str, Any]) -> None:
    """Print configuration summary.

    Args:
        answers: Dictionary with all user answers
    """
    print_step(7, 7, "Review & Confirm")

    console.print("[bold]Configuration Summary:[/bold]\n")

    console.print(f"  Company: [cyan]{answers['company']['company_name']}[/cyan]")
    if answers["company"]["contact_email"]:
        console.print(f"  Email: {answers['company']['contact_email']}")
    if answers["company"]["contact_phone"]:
        console.print(f"  Phone: {answers['company']['contact_phone']}")

    console.print(f"\n  Workspaces: [cyan]{len(answers['organization']['workspaces'])}[/cyan]")
    for ws in answers["organization"]["workspaces"][:5]:
        console.print(f"    • {ws}")
    if len(answers["organization"]["workspaces"]) > 5:
        console.print(f"    • ... and {len(answers['organization']['workspaces']) - 5} more")

    console.print(f"\n  Roles: [cyan]{len(answers['organization']['roles'])}[/cyan]")
    for role in answers["organization"]["roles"][:5]:
        console.print(f"    • {role}")
    if len(answers["organization"]["roles"]) > 5:
        console.print(f"    • ... and {len(answers['organization']['roles']) - 5} more")

    console.print(
        f"\n  Alerts: Critical=[cyan]{answers['alerts']['critical_days']}d[/cyan], "
        f"Warning=[cyan]{answers['alerts']['warning_days']}d[/cyan], "
        f"Info=[cyan]{answers['alerts']['info_days']}d[/cyan]"
    )

    console.print(f"\n  Database: [cyan]{answers['database']['database_filename']}[/cyan]")
    console.print(
        f"  Backups: [cyan]{'Enabled' if answers['database']['enable_auto_backup'] else 'Disabled'}[/cyan]"
    )
    if answers["database"]["enable_auto_backup"]:
        console.print(f"  Retention: [cyan]{answers['database']['backup_retention']} days[/cyan]")

    console.print(f"\n  Theme: [cyan]{answers['interface']['theme'].capitalize()}[/cyan]")

    console.print("")


def confirm_configuration(answers: Dict[str, Any]) -> bool:
    """Ask user to confirm configuration.

    Args:
        answers: Dictionary with all user answers

    Returns:
        True if user confirms, False otherwise
    """
    print_summary(answers)

    confirmed = questionary.confirm(
        "Configuration looks correct?",
        default=True,
        instruction="Press Enter to confirm, ESC to edit",
    ).ask()

    return confirmed


def build_config_dict(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Build configuration dictionary from wizard answers.

    Args:
        answers: Dictionary with all user answers

    Returns:
        Configuration dictionary compatible with config module
    """
    return {
        "organization": {
            "company_name": answers["company"]["company_name"],
            "contact_email": answers["company"]["contact_email"],
            "contact_phone": answers["company"]["contact_phone"],
            "workspaces": answers["organization"]["workspaces"],
            "roles": answers["organization"]["roles"],
        },
        "alerts": {
            "critical_days": answers["alerts"]["critical_days"],
            "warning_days": answers["alerts"]["warning_days"],
            # info_days is stored but not used by core config yet
        },
        "lock": {
            "timeout_minutes": 2,
            "heartbeat_interval_seconds": 30,
        },
    }


def save_config(cfg: Dict[str, Any], config_path: Path) -> None:
    """Save configuration to YAML file.

    Args:
        cfg: Configuration dictionary
        config_path: Path where to save config.yaml
    """
    config.save_config(cfg, config_path, format="yaml")
    console.print(f"✅ [green]Configuration saved to {config_path}[/green]")


def create_directory_structure(base_dir: Path) -> None:
    """Create required directory structure.

    Args:
        base_dir: Base directory for installation
    """
    directories = [
        base_dir / "data",
        base_dir / "documents",
        base_dir / "documents" / "caces",
        base_dir / "documents" / "medical",
        base_dir / "documents" / "training",
        base_dir / "backups",
        base_dir / "logs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    console.print(f"✅ [green]Directory structure created[/green]")


def run_setup_wizard(config_path: Path | None = None) -> Dict[str, Any]:
    """Run the interactive setup wizard.

    This guides users through configuration step by step, validates input,
    and creates the configuration file and directory structure.

    Args:
        config_path: Path where to save config.yaml (default: ./config.yaml)

    Returns:
        Configuration dictionary that was created

    Example:
        >>> from bootstrapper.wizard import run_setup_wizard
        >>> config = run_setup_wizard()
        >>> print(f"Company: {config['organization']['company_name']}")
    """
    if config_path is None:
        config_path = Path("config.yaml")

    # Check if config already exists
    if config_path.exists():
        overwrite = questionary.confirm(
            f"Configuration file already exists at {config_path}",
            default=False,
            instruction="Overwrite existing configuration?",
        ).ask()

        if not overwrite:
            console.print("[yellow]Setup wizard cancelled.[/yellow]")
            return {}

    # Print welcome header
    print_header()

    # Collect all answers
    answers = {
        "company": ask_company_info(),
        "organization": ask_organization(),
        "alerts": ask_alerts(),
        "database": ask_database(),
        "interface": ask_interface(),
        "advanced": ask_advanced(),
    }

    # Confirm configuration
    while not confirm_configuration(answers):
        # User wants to edit - restart wizard
        console.print("\n[yellow]Restarting wizard...[/yellow]\n")
        return run_setup_wizard(config_path)

    # Build configuration dictionary
    cfg = build_config_dict(answers)

    # Save configuration
    save_config(cfg, config_path)

    # Create directory structure
    create_directory_structure(Path("."))

    # Success message
    console.print("\n")
    success_panel = Panel(
        "[bold green]✅ Setup complete![/bold green]\n\n"
        f"Configuration: [cyan]{config_path}[/cyan]\n"
        "Database: Will be created on first run\n\n"
        "[dim]You can now start the application with:[/dim]\n"
        "[bold]wems[/bold] or [bold]wems-gui[/bold]",
        title="[bold blue]Success[/bold blue]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(success_panel)

    return cfg
