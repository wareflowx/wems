"""Online training management commands."""

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from cli.utils import format_training_table
from database.connection import database as db
from employee.models import Employee, OnlineTraining

app = typer.Typer(help="Gestion des formations en ligne")


@app.command()
def list(employee_id: str = typer.Argument(..., help="ID WMS de l'employé")):
    """Lister toutes les formations d'un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    trainings = [t for t in employee.trainings]

    if not trainings:
        typer.echo(f"Aucune formation pour {employee.full_name}")
        raise typer.Exit(0)

    typer.echo(f"Formations pour {employee.full_name} ({employee_id})")
    typer.echo("")
    typer.echo(format_training_table(trainings))


@app.command()
def add(
    employee_id: str = typer.Argument(..., help="ID WMS de l'employé"),
    title: str = typer.Option(..., "--title", "-t", help="Titre de la formation"),
    completion_date: str = typer.Option(..., "--completion-date", "-d", help="Date de complétion (YYYY-MM-DD)"),
    validity_months: Optional[int] = typer.Option(None, "--validity-months", "-m", help="Mois de validité"),
    permanent: bool = typer.Option(False, "--permanent", help="Formation permanente (pas d'expiration)"),
    certificate: Optional[Path] = typer.Option(None, "--certificate", help="Chemin du certificat PDF"),
):
    """Ajouter une formation à un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Validate exclusivity
    if permanent and validity_months:
        typer.echo("❌ Spécifiez soit --permanent soit --validity-months, pas les deux", err=True)
        raise typer.Exit(1)

    if not permanent and not validity_months:
        typer.echo("❌ Spécifiez soit --permanent soit --validity-months", err=True)
        raise typer.Exit(1)

    # Parse date
    try:
        completion_date_obj = date.fromisoformat(completion_date)
    except ValueError:
        typer.echo(f"❌ Format de date invalide: {completion_date}. Utilisez YYYY-MM-DD", err=True)
        raise typer.Exit(1)

    # Certificate path
    certificate_path = str(certificate) if certificate else None

    # Create training
    try:
        with db.atomic():
            training = OnlineTraining.create(
                employee=employee,
                title=title,
                completion_date=completion_date_obj,
                validity_months=None if permanent else validity_months,
                certificate_path=certificate_path,
            )

        typer.echo("✅ Formation ajoutée")
        typer.echo(f"   Employé: {employee.full_name} ({employee_id})")
        typer.echo(f"   Titre: {training.title}")
        typer.echo(f"   Complétion: {training.completion_date}")
        if training.expires:
            typer.echo(f"   Expiration: {training.expiration_date}")
            typer.echo(f"   Statut: {'🟢 Valide' if not training.is_expired else '🔴 Expiré'}")
        else:
            typer.echo(f"   Statut: 🟢 Permanent")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la création: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    training_id: int = typer.Argument(..., help="ID de la formation"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Nouveau titre"),
    completion_date: Optional[str] = typer.Option(
        None, "--completion-date", "-d", help="Nouvelle date de complétion (YYYY-MM-DD)"
    ),
    validity_months: Optional[int] = typer.Option(None, "--validity-months", "-m", help="Nouveaux mois de validité"),
    permanent: bool = typer.Option(False, "--permanent", help="Rendre permanente"),
    certificate: Optional[Path] = typer.Option(None, "--certificate", help="Nouveau chemin du certificat"),
):
    """Mettre à jour une formation."""
    training = OnlineTraining.get_or_none(OnlineTraining.id == training_id)

    if not training:
        typer.echo(f"❌ Formation {training_id} non trouvée", err=True)
        raise typer.Exit(1)

    # Track changes
    changes = []

    if title is not None and isinstance(title, str):
        training.title = title
        changes.append(f"Titre → {title}")

    if completion_date is not None and isinstance(completion_date, str):
        try:
            new_date = date.fromisoformat(completion_date)
            training.completion_date = new_date
            changes.append(f"Complétion → {completion_date}")
        except ValueError:
            typer.echo(f"❌ Format de date invalide: {completion_date}. Utilisez YYYY-MM-DD", err=True)
            raise typer.Exit(1)

    if permanent:
        training.validity_months = None
        changes.append("Statut → Permanent")

    if validity_months is not None and isinstance(validity_months, int):
        training.validity_months = validity_months
        changes.append(f"Validité → {validity_months} mois")

    if certificate is not None:
        training.certificate_path = str(certificate)
        changes.append(f"Certificat → {certificate}")

    if not changes:
        typer.echo("ℹ️  Aucun changement à effectuer")
        raise typer.Exit(0)

    # Save changes
    try:
        training.save()
        typer.echo("✅ Formation mise à jour")
        for change in changes:
            typer.echo(f"   {change}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la mise à jour: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    training_id: int = typer.Argument(..., help="ID de la formation"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmer sans prompt"),
):
    """Supprimer une formation."""
    training = OnlineTraining.get_or_none(OnlineTraining.id == training_id)

    if not training:
        typer.echo(f"❌ Formation {training_id} non trouvée", err=True)
        raise typer.Exit(1)

    employee = training.employee

    # Confirm deletion
    if not yes:
        try:
            import questionary

            confirm = questionary.confirm(
                f"Supprimer la formation '{training.title}' (ID: {training_id})?", default=False
            ).ask()

            if not confirm:
                typer.echo("❌ Suppression annulée")
                raise typer.Exit(0)

        except ImportError:
            typer.echo(f"⚠️  Pour supprimer la formation, utilisez --yes")
            raise typer.Exit(1)

    # Delete training
    try:
        with db.atomic():
            training.delete_instance()

        typer.echo(f"✅ Formation {training_id} supprimée")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la suppression: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def expiring(days: int = typer.Option(30, "--days", "-d", help="Jours avant expiration")):
    """Afficher les formations expirant bientôt."""
    threshold = date.today()

    expiring_trainings = []
    for training in OnlineTraining.select():
        if training.expires:
            if training.expiration_date <= threshold and not training.is_expired:
                if training.days_until_expiration <= days:
                    expiring_trainings.append(training)

    if not expiring_trainings:
        typer.echo(f"✅ Aucune formation expirant dans les {days} prochains jours")
        raise typer.Exit(0)

    typer.echo(f"🔔 Formations expirant dans les {days} prochains jours ({len(expiring_trainings)})")
    typer.echo("")
    typer.echo(format_training_table(expiring_trainings))
