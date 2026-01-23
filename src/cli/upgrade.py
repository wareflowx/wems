"""Database migration upgrade command.

Provides the `upgrade` CLI command to apply pending database migrations
with automatic backup and rollback capability.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.connection import database
from database.migrations import (
    MigrationError,
    backup_database,
    get_pending_migrations,
    run_migration,
)
from database.migration_model import get_applied_migrations, get_last_batch_number
from utils.logging_config import setup_logging, get_logger

app = typer.Typer(help="Database migration management")
console = Console()

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)


def get_database_path() -> Path:
    """Get the database file path.

    Returns:
        Path to the database file
    """
    # Get database path from connection
    db_path = database.database
    if db_path is None or db_path == ":memory:":
        raise typer.BadParameter("Database not initialized or is in-memory mode")

    return Path(db_path)


def print_migration_plan(pending_migrations: list) -> None:
    """Print migration plan in a formatted table.

    Args:
        pending_migrations: List of pending migrations
    """
    table = Table(title="Pending Migrations", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Migration Name", style="cyan")
    table.add_column("Description", style="green")

    for i, migration in enumerate(pending_migrations, 1):
        # Extract description from migration name
        parts = migration.name.split("_", 2)
        description = parts[2].replace("_", " ").title() if len(parts) > 2 else "N/A"

        table.add_row(str(i), f"[cyan]{migration.name}[/cyan]", description)

    console.print(table)


@app.command()
def upgrade(
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview migrations without applying"),
    no_backup: bool = typer.Option(False, "--no-backup", help="Skip automatic backup"),
    force: bool = typer.Option(False, "--force", help="Run even if pre-checks fail"),
):
    """Apply pending database migrations.

    This command will:
    1. Check for pending migrations
    2. Create a backup (unless --no-backup)
    3. Apply migrations sequentially
    4. Validate each migration

    Example:
        $ wems upgrade --dry-run        # Preview migrations
        $ wems upgrade                   # Apply migrations
        $ wems upgrade --no-backup       # Apply without backup
    """
    try:
        # Get database path
        db_path = get_database_path()

        # Get pending migrations
        migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        pending = get_pending_migrations(migrations_dir)
        applied = get_applied_migrations()

        # Print status
        console.print(f"[dim]Database:[/dim] {db_path}")
        console.print(f"[dim]Applied migrations:[/dim] {len(applied)}")
        console.print(f"[dim]Pending migrations:[/dim] {len(pending)}")

        if not pending:
            console.print("[green]✓[/green] Database is up to date!")
            raise typer.Exit(0)

        # Show migration plan
        console.print()
        print_migration_plan(pending)

        if dry_run:
            console.print()
            console.print(Panel(
                "[yellow]DRY RUN MODE[/yellow]\n\n"
                "No changes will be made.\n"
                "Run without --dry-run to apply these migrations.",
                title_style="yellow"
            ))
            raise typer.Exit(0)

        # Confirm before proceeding
        console.print()
        confirm = typer.confirm(f"Apply {len(pending)} migration(s)?")
        if not confirm:
            console.print("[yellow]Upgrade cancelled[/yellow]")
            raise typer.Exit(0)

        # Create backup
        if not no_backup:
            console.print()
            with console.status("[bold cyan]Creating backup...", spinner="dots"):
                backup_path = backup_database(db_path)
            console.print(f"[green]✓[/green] Backup created: {backup_path}")
        else:
            console.print("[yellow]⚠[/yellow] Skipping backup (--no-backup)")
            backup_path = None

        # Get batch number
        batch = get_last_batch_number() + 1

        # Apply migrations
        console.print()
        console.print("[bold]Applying migrations[/bold]")

        success_count = 0
        failed_migrations = []

        for i, migration in enumerate(pending, 1):
            try:
                with console.status(
                    f"[bold cyan][{i}/{len(pending)}] Applying {migration.name}...",
                    spinner="dots"
                ):
                    run_migration(migration, batch)

                console.print(f"[green]✓[/green] [{i}/{len(pending)}] {migration.name}")
                success_count += 1

            except MigrationError as e:
                console.print(f"[red]✗[/red] [{i}/{len(pending)}] {migration.name}")
                console.print(f"[red]  Error: {e}[/red]")
                failed_migrations.append((migration, str(e)))

                # Stop on first failure
                break

        # Summary
        console.print()
        if success_count == len(pending):
            console.print(Panel(
                f"[green]✓ Upgrade Complete![/green]\n\n"
                f"Applied: {success_count} migration(s)\n"
                f"Batch: {batch}",
                title="Success"
            ))

            if backup_path:
                console.print(f"\n[dim]Backup saved:[/dim] {backup_path}")
                console.print("[dim]If you encounter issues, you can rollback using:[/dim]")
                console.print(f"  [cyan]wems rollback --batch {batch}[/cyan]")

            raise typer.Exit(0)

        else:
            console.print(Panel(
                f"[red]✗ Upgrade Failed[/red]\n\n"
                f"Applied: {success_count}/{len(pending)} migration(s)\n"
                f"Failed: {len(failed_migrations)} migration(s)",
                title="Error",
                border_style="red"
            ))

            if failed_migrations:
                console.print("\n[red]Failed migrations:[/red]")
                for migration, error in failed_migrations:
                    console.print(f"  [red]•[/red] {migration.name}")
                    console.print(f"    {error}")

            if backup_path:
                console.print(f"\n[dim]Backup available:[/dim] {backup_path}")
                console.print("[dim]You can rollback the applied migrations with:[/dim]")
                console.print(f"  [cyan]wems rollback --batch {batch}[/cyan]")

            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]✗ Upgrade failed:[/red] {e}")
        logger.error(f"Upgrade failed: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def status():
    """Show migration status."""
    try:
        # Get database path
        db_path = get_database_path()

        # Get migrations
        migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        from database.migrations import discover_migrations
        migration_files = discover_migrations(migrations_dir)
        applied = get_applied_migrations()
        pending = get_pending_migrations(migrations_dir)

        # Print status
        console.print()
        console.print(f"[dim]Database:[/dim] {db_path}")
        console.print()

        # Summary table
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total migrations", str(len(migration_files)))
        table.add_row("Applied migrations", str(len(applied)))
        table.add_row("Pending migrations", str(len(pending)))

        console.print(table)

        # Show pending migrations if any
        if pending:
            console.print()
            print_migration_plan(pending)
        else:
            console.print()
            console.print("[green]✓ Database is up to date![/green]")

    except Exception as e:
        console.print(f"[red]✗ Failed to get status:[/red] {e}")
        logger.error(f"Status check failed: {e}", exc_info=True)
        raise typer.Exit(1)
