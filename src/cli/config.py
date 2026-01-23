"""Configuration management commands for CLI.

This module provides commands for initializing, managing, and validating
Wareflow EMS configuration files.

Usage:
    wems config init          # Run interactive setup wizard
    wems config init --defaults  # Generate config with defaults
    wems config validate       # Validate existing configuration
    wems config show           # Display current configuration
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bootstrapper.wizard import run_setup_wizard
from cli.utils import console as cli_console
from utils import config

app = typer.Typer(
    help="Configuration management commands",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    defaults: bool = typer.Option(
        False,
        "--defaults",
        "-d",
        help="Generate configuration with default values (no wizard)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration file",
    ),
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
    ),
) -> None:
    """Initialize Wareflow EMS configuration.

    Run the interactive setup wizard to create a new configuration file,
    or generate one with default values.

    Examples:
        # Run interactive wizard
        wems config init

        # Generate with defaults (no prompts)
        wems config init --defaults

        # Specify custom config path
        wems config init --config /path/to/config.yaml

        # Overwrite existing config
        wems config init --force
    """
    if config_path is None:
        config_path = Path("config.yaml")

    # Check if config exists
    if config_path.exists() and not force:
        console.print(
            f"[yellow]Configuration file already exists: {config_path}[/yellow]"
        )
        overwrite = typer.confirm("Overwrite existing configuration?", default=False)
        if not overwrite:
            console.print("[dim]Aborted.[/dim]")
            raise typer.Exit(0)

    console.print("\n[bold cyan]Wareflow EMS Configuration[/bold cyan]")
    console.print("[dim]" + "=" * 40 + "[/dim]\n")

    if defaults:
        # Generate default configuration
        console.print("[dim]Generating configuration with default values...[/dim]\n")

        cfg = config.get_default_config()
        config.save_config(cfg, config_path, format="yaml")

        console.print(f"✅ [green]Configuration saved to: {config_path}[/green]")
        console.print(
            "\n[dim]Edit the configuration file to customize settings,[/dim]"
        )
        console.print("[dim]then run: wems start[/dim]")
    else:
        # Run interactive wizard
        try:
            run_setup_wizard(config_path)
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Setup cancelled by user.[/yellow]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n\n[red]Error during setup: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def validate(
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
    ),
) -> None:
    """Validate configuration file.

    Check if the configuration file is valid and follows the expected schema.

    Examples:
        # Validate default config file
        wems config validate

        # Validate specific file
        wems config validate --config /path/to/config.yaml
    """
    if config_path is None:
        # Try to find config file
        for filename in ["config.yaml", "config.yml", "config.json"]:
            test_path = Path(filename)
            if test_path.exists():
                config_path = test_path
                break
        else:
            console.print("[red]No configuration file found.[/red]")
            console.print("[dim]Run 'wems config init' to create one.[/dim]")
            raise typer.Exit(1)

    # Validate format
    try:
        fmt = config._detect_format(config_path)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Load configuration
    try:
        cfg = config.load_config(config_path)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(1)

    # Validate content
    is_valid, errors = config.validate_config(cfg)

    if is_valid:
        console.print(f"✅ [green]Configuration is valid![/green]")
        console.print(f"   Format: [cyan]{fmt.upper()}[/cyan]")
        console.print(f"   Path: [cyan]{config_path}[/cyan]")
    else:
        console.print(f"[red]Configuration validation failed:[/red]")
        for error in errors:
            console.print(f"  • [red]✗[/red] {error}")
        raise typer.Exit(1)


@app.command()
def show(
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
    ),
) -> None:
    """Display current configuration.

    Show the current configuration values in a formatted table.

    Examples:
        # Show default config
        wems config show

        # Show specific file
        wems config show --config /path/to/config.yaml
    """
    if config_path is None:
        cfg = config.load_config()
    else:
        cfg = config.load_config(config_path)

    # Create table
    table = Table(title=f"Configuration: {config_path or 'Default'}")

    table.add_column("Section", style="cyan", no_wrap=True)
    table.add_column("Key", style="green")
    table.add_column("Value", style="yellow")

    # Alerts section
    table.add_row("Alerts", "Critical days", str(cfg.get("alerts", {}).get("critical_days", "N/A")))
    table.add_row("", "Warning days", str(cfg.get("alerts", {}).get("warning_days", "N/A")))

    # Lock section
    table.add_row("Lock", "Timeout (minutes)", str(cfg.get("lock", {}).get("timeout_minutes", "N/A")))
    table.add_row("", "Heartbeat (seconds)", str(cfg.get("lock", {}).get("heartbeat_interval_seconds", "N/A")))

    # Organization section
    roles = cfg.get("organization", {}).get("roles", [])
    workspaces = cfg.get("organization", {}).get("workspaces", [])

    table.add_row("Organization", "Roles", f"{len(roles)} roles")
    for role in roles[:3]:
        table.add_row("", "", f"  • {role}")
    if len(roles) > 3:
        table.add_row("", "", f"  • ... and {len(roles) - 3} more")

    table.add_row("", "Workspaces", f"{len(workspaces)} workspaces")
    for ws in workspaces[:3]:
        table.add_row("", "", f"  • {ws}")
    if len(workspaces) > 3:
        table.add_row("", "", f"  • ... and {len(workspaces) - 3} more")

    console.print(table)


@app.command()
def migrate(
    json_path: Path = typer.Argument(
        ...,
        help="Path to JSON configuration file",
        exists=True,
    ),
    yaml_path: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Path for new YAML file (default: same name with .yaml extension)",
    ),
) -> None:
    """Migrate JSON configuration to YAML format.

    Convert an existing JSON configuration file to YAML with helpful comments.

    Examples:
        # Migrate config.json to config.yaml
        wems config migrate config.json

        # Migrate to custom path
        wems config migrate config.json --output custom_config.yaml
    """
    try:
        result_path = config.migrate_to_yaml(json_path, yaml_path)
        console.print(f"✅ [green]Migrated configuration:[/green]")
        console.print(f"   [cyan]JSON:[/cyan] {json_path}")
        console.print(f"   [cyan]YAML:[/cyan] {result_path}")
        console.print(
            "\n[dim]💡 Tip: Review the YAML file and add your comments,[/dim]"
        )
        console.print("[dim]then delete the old JSON file if everything looks good.[/dim]")
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during migration: {e}[/red]")
        raise typer.Exit(1)
