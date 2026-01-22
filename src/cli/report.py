"""Report and export commands."""

from pathlib import Path
from typing import Optional

import typer

from cli.utils import format_alerts, format_dashboard
from database.connection import database as db
from employee import calculations, queries
from employee.models import Employee
from export import excel

app = typer.Typer(help="Rapports et exports")


@app.command()
def dashboard():
    """Afficher le tableau de bord avec statistiques."""
    # Calculate statistics
    total_employees = Employee.select().count()
    active_employees = Employee.select().where(Employee.current_status == "active").count()

    # Count expiring items
    expired_caces = 0
    critical_caces = 0
    expired_visits = 0
    critical_visits = 0
    expired_trainings = 0
    critical_trainings = 0

    employees = [e for e in Employee.select()]

    for emp in employees:
        # CACES
        for caces in emp.caces:
            if caces.is_expired:
                expired_caces += 1
            elif caces.status == "critical":
                critical_caces += 1

        # Medical visits
        for visit in emp.medical_visits:
            if visit.is_expired:
                expired_visits += 1
            elif visit.days_until_expiration < 30:
                critical_visits += 1

        # Trainings
        for training in emp.trainings:
            if training.expires:
                if training.is_expired:
                    expired_trainings += 1
                elif training.days_until_expiration < 30:
                    critical_trainings += 1

    unfit_count = len([v for e in employees for v in e.medical_visits if v.result == "unfit"])

    stats = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "expired_caces": expired_caces,
        "critical_caces": critical_caces,
        "expired_visits": expired_visits,
        "critical_visits": critical_visits,
        "expired_trainings": expired_trainings,
        "critical_trainings": critical_trainings,
        "unfit_count": unfit_count,
    }

    typer.echo(format_dashboard(stats))


@app.command()
def alerts(
    critical_days: int = typer.Option(7, "--critical-days", help="Jours pour alerte critique"),
    warning_days: int = typer.Option(30, "--warning-days", help="Jours pour alerte warning"),
):
    """Afficher les alertes d'items expirants."""
    employees = [e for e in Employee.select()]
    typer.echo(format_alerts(employees, critical_days, warning_days))


@app.command()
def export(
    output_path: Path = typer.Argument(..., help="Chemin de sortie du fichier Excel"),
    include_caces: bool = typer.Option(True, "--include-caces/--no-caces", help="Inclure feuille CACES"),
    include_visits: bool = typer.Option(True, "--include-visits/--no-visits", help="Inclure feuille visites"),
    include_trainings: bool = typer.Option(
        True, "--include-trainings/--no-trainings", help="Inclure feuille formations"
    ),
):
    """Exporter les données vers un fichier Excel."""
    # Validate output path
    output_path = output_path.resolve()

    # Get all employees
    employees = [e for e in Employee.select()]

    if not employees:
        typer.echo("❌ Aucun employé à exporter", err=True)
        raise typer.Exit(1)

    try:
        import time

        start_time = time.time()

        # Export
        excel.export_employees_to_excel(
            output_path=output_path,
            employees=employees,
            include_caces=include_caces,
            include_visits=include_visits,
            include_trainings=include_trainings,
        )

        elapsed = time.time() - start_time

        # Build sheet list
        sheets = ["Résumé", "Employés"]
        if include_caces:
            sheets.append("CACES")
        if include_visits:
            sheets.append("Visites Médicales")
        if include_trainings:
            sheets.append("Formations")

        typer.echo("✅ Export terminé")
        typer.echo(f"   Fichier: {output_path}")
        typer.echo(f"   Feuilles: {', '.join(sheets)}")
        typer.echo(f"   Employés: {len(employees)}")
        typer.echo(f"   Durée: {elapsed:.2f} secondes")

    except PermissionError as e:
        typer.echo(f"❌ Erreur de permission: {e}", err=True)
        typer.echo("   Fermez le fichier Excel s'il est ouvert", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Erreur lors de l'export: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def stats():
    """Afficher les statistiques globales."""
    total = Employee.select().count()
    active = Employee.select().where(Employee.current_status == "active").count()

    # Count by role
    roles = {}
    for emp in Employee.select():
        role = emp.role or "Non défini"
        roles[role] = roles.get(role, 0) + 1

    # Count by workspace
    workspaces = {}
    for emp in Employee.select():
        workspace = emp.workspace or "Non défini"
        workspaces[workspace] = workspaces.get(workspace, 0) + 1

    # Display
    typer.echo("📊 Statistiques globales")
    typer.echo("")
    typer.echo(f"Employés total:  {total}")
    typer.echo(f"Employés actifs: {active}")
    typer.echo(f"Employés inactifs: {total - active}")
    typer.echo("")
    typer.echo("Par poste:")
    for role, count in sorted(roles.items(), key=lambda x: x[1], reverse=True):
        typer.echo(f"  {role}: {count}")
    typer.echo("")
    typer.echo("Par zone:")
    for workspace, count in sorted(workspaces.items(), key=lambda x: x[1], reverse=True):
        typer.echo(f"  {workspace}: {count}")


@app.command()
def unfit():
    """Lister les employés inaptes."""
    unfit_visits = []
    for emp in Employee.select():
        for visit in emp.medical_visits:
            if visit.result == "unfit":
                unfit_visits.append({"employee": emp, "visit": visit})

    if not unfit_visits:
        typer.echo("✅ Aucun employé inapte")
        raise typer.Exit(0)

    typer.echo(f"🚨 Employés inaptes ({len(unfit_visits)})")
    typer.echo("")

    for item in unfit_visits:
        emp = item["employee"]
        visit = item["visit"]
        typer.echo(f"  {emp.external_id}: {emp.full_name}")
        typer.echo(f"    Poste: {emp.role or 'N/A'}")
        typer.echo(f"    Visite: {visit.visit_type} le {visit.visit_date}")
        typer.echo(f"    Expiration: {visit.expiration_date}")
        if visit.days_until_expiration < 0:
            typer.echo(f"    ⚠️  Expirée depuis {abs(visit.days_until_expiration)} jours")
        typer.echo("")


@app.command()
def compliance_summary():
    """Afficher le résumé de compliance global."""
    employees = [e for e in Employee.select()]

    compliant_count = 0
    warning_count = 0
    critical_count = 0

    for emp in employees:
        status = calculations.get_compliance_status(emp)
        if status == "compliant":
            compliant_count += 1
        elif status == "warning":
            warning_count += 1
        elif status == "critical":
            critical_count += 1

    total = len(employees)
    if total == 0:
        typer.echo("Aucun employé")
        raise typer.Exit(0)

    compliant_pct = (compliant_count / total) * 100
    warning_pct = (warning_count / total) * 100
    critical_pct = (critical_count / total) * 100

    typer.echo("📊 Résumé de compliance")
    typer.echo("")
    typer.echo(f"  🟢 Conformes:   {compliant_count} ({compliant_pct:.1f}%)")
    typer.echo(f"  🟠 Attention:    {warning_count} ({warning_pct:.1f}%)")
    typer.echo(f"  🔴 Critiques:    {critical_count} ({critical_pct:.1f}%)")
    typer.echo("")
    typer.echo(f"  Total:          {total}")
