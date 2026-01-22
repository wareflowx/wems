"""Medical visit management commands."""

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from cli.utils import format_medical_table
from database.connection import database as db
from employee.models import Employee, MedicalVisit

app = typer.Typer(help="Gestion des visites médicales")


@app.command()
def list(employee_id: str = typer.Argument(..., help="ID WMS de l'employé")):
    """Lister toutes les visites d'un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    visits = [v for v in employee.medical_visits]

    if not visits:
        typer.echo(f"Aucune visite pour {employee.full_name}")
        raise typer.Exit(0)

    typer.echo(f"Visites médicales pour {employee.full_name} ({employee_id})")
    typer.echo("")
    typer.echo(format_medical_table(visits))


@app.command()
def add(
    employee_id: str = typer.Argument(..., help="ID WMS de l'employé"),
    visit_type: str = typer.Option(..., "--type", "-t", help="Type de visite (initial/periodic/recovery)"),
    visit_date: str = typer.Option(..., "--date", "-d", help="Date de visite (YYYY-MM-DD)"),
    result: str = typer.Option(..., "--result", "-r", help="Résultat (fit/unfit/fit_with_restrictions)"),
    document: Optional[Path] = typer.Option(None, "--document", help="Chemin du document PDF"),
):
    """Ajouter une visite médicale."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Validate visit type
    if visit_type not in ["initial", "periodic", "recovery"]:
        typer.echo("❌ Type de visite invalide. Options: initial, periodic, recovery", err=True)
        raise typer.Exit(1)

    # Validate result
    if result not in ["fit", "unfit", "fit_with_restrictions"]:
        typer.echo("❌ Résultat invalide. Options: fit, unfit, fit_with_restrictions", err=True)
        raise typer.Exit(1)

    # Parse date
    try:
        visit_date_obj = date.fromisoformat(visit_date)
    except ValueError:
        typer.echo(f"❌ Format de date invalide: {visit_date}. Utilisez YYYY-MM-DD", err=True)
        raise typer.Exit(1)

    # Document path
    document_path = str(document) if document else None

    # Create visit
    try:
        with db.atomic():
            visit = MedicalVisit.create(
                employee=employee,
                visit_type=visit_type,
                visit_date=visit_date_obj,
                result=result,
                document_path=document_path,
            )

        typer.echo("✅ Visite médicale ajoutée")
        typer.echo(f"   Employé: {employee.full_name} ({employee_id})")
        typer.echo(f"   Type: {visit.visit_type}")
        typer.echo(f"   Date: {visit.visit_date}")
        typer.echo(f"   Résultat: {visit.result}")
        typer.echo(f"   Expiration: {visit.expiration_date}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la création: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    visit_id: int = typer.Argument(..., help="ID de la visite"),
    visit_type: Optional[str] = typer.Option(None, "--type", "-t", help="Nouveau type de visite"),
    visit_date: Optional[str] = typer.Option(None, "--date", "-d", help="Nouvelle date de visite (YYYY-MM-DD)"),
    result: Optional[str] = typer.Option(None, "--result", "-r", help="Nouveau résultat"),
    document: Optional[Path] = typer.Option(None, "--document", help="Nouveau chemin du document"),
):
    """Mettre à jour une visite médicale."""
    visit = MedicalVisit.get_or_none(MedicalVisit.id == visit_id)

    if not visit:
        typer.echo(f"❌ Visite {visit_id} non trouvée", err=True)
        raise typer.Exit(1)

    # Track changes
    changes = []

    if visit_type is not None and isinstance(visit_type, str):
        if visit_type not in ["initial", "periodic", "recovery"]:
            typer.echo("❌ Type de visite invalide. Options: initial, periodic, recovery", err=True)
            raise typer.Exit(1)
        visit.visit_type = visit_type
        changes.append(f"Type → {visit_type}")

    if visit_date is not None and isinstance(visit_date, str):
        try:
            new_date = date.fromisoformat(visit_date)
            visit.visit_date = new_date
            changes.append(f"Date → {visit_date}")
        except ValueError:
            typer.echo(f"❌ Format de date invalide: {visit_date}. Utilisez YYYY-MM-DD", err=True)
            raise typer.Exit(1)

    if result is not None and isinstance(result, str):
        if result not in ["fit", "unfit", "fit_with_restrictions"]:
            typer.echo("❌ Résultat invalide. Options: fit, unfit, fit_with_restrictions", err=True)
            raise typer.Exit(1)
        visit.result = result
        changes.append(f"Résultat → {result}")

    if document is not None:
        visit.document_path = str(document)
        changes.append(f"Document → {document}")

    if not changes:
        typer.echo("ℹ️  Aucun changement à effectuer")
        raise typer.Exit(0)

    # Save changes
    try:
        visit.save()
        typer.echo("✅ Visite mise à jour")
        for change in changes:
            typer.echo(f"   {change}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la mise à jour: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    visit_id: int = typer.Argument(..., help="ID de la visite"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmer sans prompt"),
):
    """Supprimer une visite médicale."""
    visit = MedicalVisit.get_or_none(MedicalVisit.id == visit_id)

    if not visit:
        typer.echo(f"❌ Visite {visit_id} non trouvée", err=True)
        raise typer.Exit(1)

    employee = visit.employee

    # Confirm deletion
    if not yes:
        try:
            import questionary

            confirm = questionary.confirm(
                f"Supprimer la visite {visit.visit_type} du {visit.visit_date} (ID: {visit_id})?", default=False
            ).ask()

            if not confirm:
                typer.echo("❌ Suppression annulée")
                raise typer.Exit(0)

        except ImportError:
            typer.echo(f"⚠️  Pour supprimer la visite, utilisez --yes")
            raise typer.Exit(1)

    # Delete visit
    try:
        with db.atomic():
            visit.delete_instance()

        typer.echo(f"✅ Visite {visit_id} supprimée")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la suppression: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def expiring(days: int = typer.Option(30, "--days", "-d", help="Jours avant expiration")):
    """Afficher les visites expirant bientôt."""
    threshold = date.today()

    expiring_visits = []
    for visit in MedicalVisit.select():
        if visit.expiration_date <= threshold and not visit.is_expired:
            if visit.days_until_expiration <= days:
                expiring_visits.append(visit)

    if not expiring_visits:
        typer.echo(f"✅ Aucune visite expirant dans les {days} prochains jours")
        raise typer.Exit(0)

    typer.echo(f"🔔 Visites expirant dans les {days} prochains jours ({len(expiring_visits)})")
    typer.echo("")
    typer.echo(format_medical_table(expiring_visits))


@app.command()
def unfit():
    """Lister les employés inaptes."""
    unfit_visits = []
    for visit in MedicalVisit.select():
        if visit.result == "unfit":
            unfit_visits.append(visit)

    if not unfit_visits:
        typer.echo("✅ Aucun employé inapte")
        raise typer.Exit(0)

    typer.echo(f"🚨 Employés inaptes ({len(unfit_visits)})")
    typer.echo("")

    for visit in unfit_visits:
        emp = visit.employee
        typer.echo(f"  {emp.external_id}: {emp.full_name}")
        typer.echo(f"    Poste: {emp.role or 'N/A'}")
        typer.echo(f"    Visite: {visit.visit_type} le {visit.visit_date}")
        typer.echo(f"    Expiration: {visit.expiration_date}")
        if visit.is_expired:
            typer.echo(f"    ⚠️  Expirée depuis {abs(visit.days_until_expiration)} jours")
        elif visit.days_until_expiration < 30:
            typer.echo(f"    ⚠️  Expiration dans {visit.days_until_expiration} jours")
        typer.echo("")
