"""CACES certification management commands."""

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from cli.utils import format_caces_table
from database.connection import database as db
from employee.models import Caces, Employee

app = typer.Typer(help="Gestion des certifications CACES")


@app.command()
def list(employee_id: str = typer.Argument(..., help="ID WMS de l'employé")):
    """Lister tous les CACES d'un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    caces_list = [c for c in employee.caces]

    if not caces_list:
        typer.echo(f"Aucun CACES pour {employee.full_name}")
        raise typer.Exit(0)

    typer.echo(f"CACES pour {employee.full_name} ({employee_id})")
    typer.echo("")
    typer.echo(format_caces_table(caces_list))


@app.command()
def add(
    employee_id: str = typer.Argument(..., help="ID WMS de l'employé"),
    kind: str = typer.Option(..., "--kind", "-k", help="Type de CACES"),
    completion_date: str = typer.Option(..., "--completion-date", "-d", help="Date d'obtention (YYYY-MM-DD)"),
    document: Optional[Path] = typer.Option(None, "--document", help="Chemin du document PDF"),
):
    """Ajouter un CACES à un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Parse date
    try:
        completion_date = date.fromisoformat(completion_date)
    except ValueError:
        typer.echo(f"❌ Format de date invalide: {completion_date}. Utilisez YYYY-MM-DD", err=True)
        raise typer.Exit(1)

    # Document path
    document_path = str(document) if document else None

    # Create CACES
    try:
        with db.atomic():
            caces = Caces.create(
                employee=employee, kind=kind, completion_date=completion_date, document_path=document_path
            )

        typer.echo("✅ CACES ajouté")
        typer.echo(f"   Employé: {employee.full_name} ({employee_id})")
        typer.echo(f"   Type: {caces.kind}")
        typer.echo(f"   Expiration: {caces.expiration_date}")
        typer.echo(f"   Statut: {'🟢 Valide' if not caces.is_expired else '🔴 Expiré'}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la création: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    caces_id: int = typer.Argument(..., help="ID du CACES"),
    kind: Optional[str] = typer.Option(None, "--kind", "-k", help="Nouveau type de CACES"),
    completion_date: Optional[str] = typer.Option(
        None, "--completion-date", "-d", help="Nouvelle date d'obtention (YYYY-MM-DD)"
    ),
    document: Optional[Path] = typer.Option(None, "--document", help="Nouveau chemin du document"),
):
    """Mettre à jour un CACES."""
    caces = Caces.get_or_none(Caces.id == caces_id)

    if not caces:
        typer.echo(f"❌ CACES {caces_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Track changes
    changes = []

    if kind is not None and isinstance(kind, str):
        caces.kind = kind
        changes.append(f"Type → {kind}")

    if completion_date is not None and isinstance(completion_date, str):
        try:
            new_date = date.fromisoformat(completion_date)
            caces.completion_date = new_date
            changes.append(f"Date d'obtention → {completion_date}")
        except ValueError:
            typer.echo(f"❌ Format de date invalide: {completion_date}. Utilisez YYYY-MM-DD", err=True)
            raise typer.Exit(1)

    if document is not None:
        caces.document_path = str(document)
        changes.append(f"Document → {document}")

    if not changes:
        typer.echo("ℹ️  Aucun changement à effectuer")
        raise typer.Exit(0)

    # Save changes
    try:
        caces.save()
        typer.echo("✅ CACES mis à jour")
        for change in changes:
            typer.echo(f"   {change}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la mise à jour: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    caces_id: int = typer.Argument(..., help="ID du CACES"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmer sans prompt"),
):
    """Supprimer un CACES."""
    caces = Caces.get_or_none(Caces.id == caces_id)

    if not caces:
        typer.echo(f"❌ CACES {caces_id} non trouvé", err=True)
        raise typer.Exit(1)

    employee = caces.employee

    # Confirm deletion
    if not yes:
        try:
            import questionary

            confirm = questionary.confirm(f"Supprimer le CACES {caces.kind} (ID: {caces_id})?", default=False).ask()

            if not confirm:
                typer.echo("❌ Suppression annulée")
                raise typer.Exit(0)

        except ImportError:
            typer.echo(f"⚠️  Pour supprimer le CACES {caces.kind}, utilisez --yes")
            raise typer.Exit(1)

    # Delete CACES
    try:
        with db.atomic():
            caces.delete_instance()

        typer.echo(f"✅ CACES {caces_id} supprimé")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la suppression: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def expiring(days: int = typer.Option(30, "--days", "-d", help="Jours avant expiration")):
    """Afficher les CACES expirant bientôt."""
    threshold = date.today()
    cutoff = threshold

    expiring_caces = []
    for caces in Caces.select():
        if caces.expiration_date <= cutoff and not caces.is_expired:
            expiring_caces.append(caces)

    if not expiring_caces:
        typer.echo(f"✅ Aucun CACES expirant dans les {days} prochains jours")
        raise typer.Exit(0)

    typer.echo(f"🔔 CACES expirant dans les {days} prochains jours ({len(expiring_caces)})")
    typer.echo("")
    typer.echo(format_caces_table(expiring_caces))


@app.command()
def expired():
    """Afficher les CACES expirés."""
    expired_caces = [c for c in Caces.select() if c.is_expired]

    if not expired_caces:
        typer.echo("✅ Aucun CACES expiré")
        raise typer.Exit(0)

    typer.echo(f"🔴 CACES expirés ({len(expired_caces)})")
    typer.echo("")
    typer.echo(format_caces_table(expired_caces))
