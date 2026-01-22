"""Employee management commands."""

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from cli.utils import format_employee_detail, format_employee_table, get_compliance_emoji
from database.connection import database as db
from employee import calculations, queries
from employee.models import Employee

app = typer.Typer(help="Gestion des employés")


@app.command()
def list(
    active_only: bool = typer.Option(False, "--active", help="Uniquement les employés actifs"),
    status: Optional[str] = typer.Option(None, "--status", help="Filtrer par statut (active/inactive)"),
    role: Optional[str] = typer.Option(None, "--role", help="Filtrer par poste"),
    workspace: Optional[str] = typer.Option(None, "--workspace", help="Filtrer par zone"),
):
    """Lister tous les employés avec filtres optionnels."""
    # Build query
    query = Employee.select()

    if active_only or status == "active":
        query = query.where(Employee.current_status == "active")
    elif status == "inactive":
        query = query.where(Employee.current_status == "inactive")

    if role is not None and isinstance(role, str):
        query = query.where(Employee.role.contains(role))

    if workspace is not None and isinstance(workspace, str):
        query = query.where(Employee.workspace.contains(workspace))

    employees = [e for e in query]

    if not employees:
        typer.echo("Aucun employé trouvé.")
        raise typer.Exit(0)

    # Display table
    typer.echo(format_employee_table(employees))
    typer.echo(f"\nTotal: {len(employees)} employé(s)")


@app.command()
def show(employee_id: str = typer.Argument(..., help="ID WMS de l'employé")):
    """Afficher les détails d'un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    typer.echo(format_employee_detail(employee))


@app.command()
def add(
    first_name: str = typer.Option(None, "--first-name", "-f", help="Prénom"),
    last_name: str = typer.Option(None, "--last-name", "-l", help="Nom"),
    external_id: str = typer.Option(None, "--external-id", "-i", help="ID WMS"),
    workspace: str = typer.Option(None, "--workspace", "-w", help="Zone de travail"),
    role: str = typer.Option(None, "--role", "-r", help="Poste"),
    contract_type: str = typer.Option(None, "--contract", "-c", help="Type de contrat"),
    entry_date: str = typer.Option(None, "--entry-date", "-d", help="Date d'entrée (YYYY-MM-DD)"),
):
    """Ajouter un nouvel employé.

    Si aucun flag n'est fourni, mode interactif avec questionary.
    """
    # Check if running in interactive mode (no flags provided)
    if all(v is None for v in [first_name, last_name, external_id, workspace, role, contract_type, entry_date]):
        # Interactive mode
        try:
            import questionary

            first_name = questionary.text("Prénom:").ask()
            if not first_name:
                typer.echo("❌ Prénom requis", err=True)
                raise typer.Exit(1)

            last_name = questionary.text("Nom:").ask()
            if not last_name:
                typer.echo("❌ Nom requis", err=True)
                raise typer.Exit(1)

            external_id = questionary.text("ID WMS:").ask()
            if not external_id:
                typer.echo("❌ ID WMS requis", err=True)
                raise typer.Exit(1)

            workspace = questionary.select("Zone:", choices=["Quai", "Zone A", "Zone B", "Bureau"]).ask()

            role = questionary.select("Poste:", choices=["Cariste", "Préparateur", "Magasinier"]).ask()

            contract_type = questionary.select("Type de contrat:", choices=["CDI", "CDD", "Intérim"]).ask()

            entry_date_str = questionary.text(
                "Date d'entrée (YYYY-MM-DD):", validate=lambda x: len(x) == 10 if x else False
            ).ask()
            entry_date = date.fromisoformat(entry_date_str)

        except ImportError:
            typer.echo("❌ Mode interactif non disponible. Installez questionary.", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"❌ Erreur: {e}", err=True)
            raise typer.Exit(1)
    else:
        # Non-interactive mode - validate required fields
        if not all([first_name, last_name, external_id, workspace, role, contract_type, entry_date]):
            typer.echo("❌ Tous les champs sont requis en mode non-interactif", err=True)
            typer.echo(
                "   Utilisez: --first-name, --last-name, --external-id, --workspace, --role, --contract, --entry-date"
            )
            raise typer.Exit(1)

        # Parse date
        try:
            entry_date = date.fromisoformat(entry_date)
        except ValueError:
            typer.echo(f"❌ Format de date invalide: {entry_date}. Utilisez YYYY-MM-DD", err=True)
            raise typer.Exit(1)

    # Check if employee already exists
    existing = Employee.get_or_none(Employee.external_id == external_id)
    if existing:
        typer.echo(f"❌ Un employé avec l'ID {external_id} existe déjà", err=True)
        raise typer.Exit(1)

    # Create employee
    try:
        with db.atomic():
            employee = Employee.create(
                first_name=first_name,
                last_name=last_name,
                external_id=external_id,
                workspace=workspace,
                role=role,
                contract_type=contract_type,
                entry_date=entry_date,
                current_status="active",
            )

        typer.echo("✅ Employé créé avec succès")
        typer.echo(f"   ID: {employee.external_id}")
        typer.echo(f"   Nom: {employee.full_name}")
        typer.echo(f"   Statut: Actif")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la création: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    employee_id: str = typer.Argument(..., help="ID WMS de l'employé"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Nouvelle zone"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Nouveau poste"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Nouveau statut (active/inactive)"),
):
    """Mettre à jour un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Track changes
    changes = []

    if workspace is not None and isinstance(workspace, str):
        employee.workspace = workspace
        changes.append(f"Zone → {workspace}")

    if role is not None and isinstance(role, str):
        employee.role = role
        changes.append(f"Poste → {role}")

    if status is not None and isinstance(status, str):
        if status not in ["active", "inactive"]:
            typer.echo("❌ Statut doit être 'active' ou 'inactive'", err=True)
            raise typer.Exit(1)
        employee.current_status = status
        changes.append(f"Statut → {status}")

    if not changes:
        typer.echo("ℹ️  Aucun changement à effectuer")
        raise typer.Exit(0)

    # Save changes
    try:
        employee.save()
        typer.echo("✅ Employé mis à jour")
        for change in changes:
            typer.echo(f"   {change}")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la mise à jour: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    employee_id: str = typer.Argument(..., help="ID WMS de l'employé"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmer sans prompt"),
):
    """Supprimer un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Confirm deletion
    if not yes:
        try:
            import questionary

            confirm = questionary.confirm(
                f"Supprimer l'employé {employee.full_name} ({employee_id})?", default=False
            ).ask()

            if not confirm:
                typer.echo("❌ Suppression annulée")
                raise typer.Exit(0)

        except ImportError:
            typer.echo(f"⚠️  Pour supprimer {employee.full_name} ({employee_id}), utilisez --yes")
            raise typer.Exit(1)

    # Delete employee
    try:
        with db.atomic():
            # Cascade delete will handle related records
            employee.delete_instance()

        typer.echo(f"✅ Employé {employee_id} supprimé")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la suppression: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def compliance(employee_id: str = typer.Argument(..., help="ID WMS de l'employé")):
    """Afficher le score de compliance d'un employé."""
    employee = Employee.get_or_none(Employee.external_id == employee_id)

    if not employee:
        typer.echo(f"❌ Employé {employee_id} non trouvé", err=True)
        raise typer.Exit(1)

    # Calculate compliance
    status = calculations.get_compliance_status(employee)
    score_data = calculations.calculate_compliance_score(employee)
    emoji = get_compliance_emoji(status)

    # Display
    lines = [
        f"┌─────────────────────────────────────────────────────────┐",
        f"│  Compliance: {employee.full_name} ({employee.external_id})".ljust(58) + "│",
        f"├─────────────────────────────────────────────────────────┤",
        f"│  Score:        {score_data['score']}/100".ljust(58) + "│",
        f"│  Statut:       {emoji} {status.capitalize()}".ljust(58) + "│",
        f"│                                                         │",
        f"│  Détails:                                               │",
        f"│  ├─ CACES:        {len(employee.caces)} certification(s)".ljust(58) + "│",
        f"│  ├─ Visites:      {len(employee.medical_visits)} visite(s)".ljust(58) + "│",
        f"│  └─ Formations:   {len(employee.trainings)} formation(s)".ljust(58) + "│",
        f"│                                                         │",
        f"│  Items:                                                 │",
        f"│  ├─ Valides:     {score_data['valid_items']}".ljust(58) + "│",
        f"│  ├─ Critiques:   {score_data['critical_items']}".ljust(58) + "│",
        f"│  └─ Expirés:     {score_data['expired_items']}".ljust(58) + "│",
        f"└─────────────────────────────────────────────────────────┘",
    ]

    typer.echo("\n".join(lines))

    # Show next actions if any
    actions = calculations.calculate_next_actions(employee)
    if actions:
        typer.echo("\n📋 Actions requises:")
        for action in actions[:5]:  # Limit to 5 actions
            priority_emoji = "🔴" if action["priority"] == "urgent" else "🟠" if action["priority"] == "high" else "🟢"
            typer.echo(f"  {priority_emoji} {action['description']}")
    else:
        typer.echo("\n✅ Aucune action requise")
