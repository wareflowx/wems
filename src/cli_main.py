"""Simple Employee Manager - CLI entry point.

This module provides the main CLI application using Typer.
All subcommands are organized into separate modules.
"""

import typer

from cli import caces, employee, lock, medical, report, training

# Main application
app = typer.Typer(
    name="employee-manager",
    help="Simple Employee Manager - Gestion des employés et certifications",
    no_args_is_help=True,
    add_completion=True,
)

# Register command groups
app.add_typer(employee.app, name="employee", help="Gestion des employés")
app.add_typer(caces.app, name="caces", help="Gestion des certifications CACES")
app.add_typer(medical.app, name="medical", help="Gestion des visites médicales")
app.add_typer(training.app, name="training", help="Gestion des formations en ligne")
app.add_typer(report.app, name="report", help="Rapports et exports")
app.add_typer(lock.app, name="lock", help="Gestion du verrou applicatif")


@app.command()
def version():
    """Show application version."""
    from employee_manager import __version__

    typer.echo(f"Simple Employee Manager v{__version__}")


if __name__ == "__main__":
    app()


def cli_main():
    """Entry point for console script."""
    app()
