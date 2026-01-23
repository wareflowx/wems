"""Database migration rollback command.

Provides the `rollback` CLI command to rollback migrations with safety checks.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.connection import database as db
from database.migrations import (
    RollbackError,
    discover_migrations,
    restore_database,
    rollback_migration,
)
from database.migration_model import Migration, get_last_batch_number
from utils.logging_config import get_logger

app = typer.Typer(help="Rollback database migrations")
console = Console()
logger = get_logger(__name__)


def get_database_path() -> Path:
    """Get the database file path.

    Returns:
        Path to the database file
    """
    # Get database path from connection
    db_path = db.database
    if db_path is None or db_path == ":memory:":
        raise typer.BadParameter("Database not initialized or is in-memory mode")

    return Path(db_path)


@app.command()
def rollback(
    batch: Optional[int] = typer.Option(None, "--batch", "-b", help="Rollback specific batch"),
    step: int = typer.Option(1, "--step", "-s", help="Number of migrations to rollback (default: 1)"),
    backup: Optional[Path] = typer.Option(None, "--backup", help="Restore from backup file instead"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
):
    """Rollback database migrations.

    This command will:
    1. Show migrations to be rolled back
    2. Confirm before proceeding (unless --force)
    3. Rollback migrations in reverse order

    Examples:
        $ wems rollback                    # Rollback last migration
        $ wems rollback --step 3           # Rollback last 3 migrations
        $ wems rollback --batch 5          # Rollback entire batch 5
        $ wems rollback --backup backups/before_migration_20250123.db
    """
    try:
        # Get database path
        db_path = get_database_path()

        if backup:
            # Restore from backup file
            if not backup.exists():
                console.print(f"[red]✗ Backup file not found:[/red] {backup}")
                raise typer.Exit(1)

            console.print()
            console.print(Panel(
                f"[yellow]⚠ RESTORE FROM BACKUP[/yellow]\n\n"
                f"This will restore the database from:\n  [cyan]{backup}[/cyan]\n\n"
                f"[dim]Current database:[/dim] {db_path}\n\n"
                f"[red]All changes since the backup will be LOST![/red]",
                border_style="yellow"
            ))

            if not force:
                confirm = typer.confirm("Are you sure you want to restore from backup?")
                if not confirm:
                    console.print("[yellow]Rollback cancelled[/yellow]")
                    raise typer.Exit(0)

            with console.status("[bold cyan]Restoring database...", spinner="dots"):
                restore_database(backup, db_path)

            console.print(f"[green]✓[/green] Database restored from {backup}")
            console.print("[dim]Restart application to use restored database[/dim]")
            raise typer.Exit(0)

        # Rollback migrations
        if batch is not None:
            # Rollback entire batch
            migrations_to_rollback = Migration.select().where(Migration.batch == batch)
            count = migrations_to_rollback.count()

            if count == 0:
                console.print(f"[yellow]No migrations found in batch {batch}[/yellow]")
                raise typer.Exit(0)

            console.print()
            console.print(f"[dim]Rolling back {count} migration(s) from batch {batch}[/dim]")

        else:
            # Rollback last N migrations
            last_batch = get_last_batch_number()
            if last_batch == 0:
                console.print("[yellow]No migrations to rollback[/yellow]")
                raise typer.Exit(0)

            # Get migrations from last batch(s)
            migrations_to_rollback = (
                Migration.select()
                .order_by(Migration.id.desc())
                .limit(step)
            )

            count = migrations_to_rollback.count()
            if count == 0:
                console.print("[yellow]No migrations to rollback[/yellow]")
                raise typer.Exit(0)

            console.print()
            console.print(f"[dim]Rolling back {count} migration(s)[/dim]")

        # Show migrations to rollback
        console.print()
        table = Table(title="Migrations to Rollback", show_header=True, header_style="bold red")
        table.add_column("Migration Name", style="cyan")
        table.add_column("Applied At", style="dim")
        table.add_column("Batch", style="yellow")

        for migration in migrations_to_rollback:
            table.add_row(
                f"[cyan]{migration.name}[/cyan]",
                migration.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
                str(migration.batch)
            )

        console.print(table)

        # Confirm
        if not force:
            console.print()
            confirm = typer.confirm("Rollback these migrations?")
            if not confirm:
                console.print("[yellow]Rollback cancelled[/yellow]")
                raise typer.Exit(0)

        # Load migration classes
        migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        migration_files = discover_migrations(migrations_dir)

        # Build mapping of migration names to classes
        migration_map = {}
        for migration_file in migration_files:
            migration_name = migration_file.stem

            try:
                import importlib
                module_name = f"database.migrations.{migration_name}"
                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and hasattr(attr, '__bases__')
                        and attr.__name__ != 'BaseMigration'
                    ):
                        # Check if it has the name property
                        if hasattr(attr, 'name'):
                            instance = attr()
                            migration_map[instance.name] = instance
                            break

            except Exception as e:
                logger.warning(f"Failed to load migration {migration_name}: {e}")

        # Rollback migrations in reverse order of application
        console.print()
        success_count = 0
        failed_migrations = []

        # Convert to list and reverse
        migrations_list = list(migrations_to_rollback)
        migrations_list.reverse()

        for i, migration_record in enumerate(migrations_list, 1):
            migration_name = migration_record.name

            if migration_name not in migration_map:
                console.print(
                    f"[yellow]⚠[/yellow] [{i}/{len(migrations_list)}] "
                    f"{migration_name} - Migration class not found, skipping record removal"
                )
                # Remove record but can't rollback
                from database.migration_model import delete_migration
                delete_migration(migration_name)
                success_count += 1
                continue

            migration_instance = migration_map[migration_name]

            try:
                with console.status(
                    f"[bold yellow][{i}/{len(migrations_list)}] Rolling back {migration_name}...",
                    spinner="dots"
                ):
                    rollback_migration(migration_instance)

                console.print(f"[green]✓[/green] [{i}/{len(migrations_list)}] {migration_name}")
                success_count += 1

            except RollbackError as e:
                console.print(f"[red]✗[/red] [{i}/{len(migrations_list)}] {migration_name}")
                console.print(f"[red]  Error: {e}[/red]")
                failed_migrations.append((migration_name, str(e)))

                # Stop on first failure
                break

        # Summary
        console.print()
        if success_count == len(migrations_list):
            console.print(Panel(
                f"[green]✓ Rollback Complete![/green]\n\n"
                f"Rolled back: {success_count} migration(s)",
                title="Success"
            ))
            console.print("[dim]Restart application to use rolled back database[/dim]")
            raise typer.Exit(0)

        else:
            console.print(Panel(
                f"[red]✗ Rollback Failed[/red]\n\n"
                f"Rolled back: {success_count}/{len(migrations_list)} migration(s)\n"
                f"Failed: {len(failed_migrations)} migration(s)",
                title="Error",
                border_style="red"
            ))

            if failed_migrations:
                console.print("\n[red]Failed rollbacks:[/red]")
                for name, error in failed_migrations:
                    console.print(f"  [red]•[/red] {name}")
                    console.print(f"    {error}")

            console.print("\n[dim]You may need to restore from backup if rollback failed.[/dim]")

            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]✗ Rollback failed:[/red] {e}")
        logger.error(f"Rollback failed: {e}", exc_info=True)
        raise typer.Exit(1)
