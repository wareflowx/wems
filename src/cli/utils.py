"""CLI utility functions for formatting and display."""

from typing import Any

from tabulate import tabulate


def get_compliance_emoji(status: str) -> str:
    """
    Return emoji based on compliance status.

    Args:
        status: Compliance status ('critical', 'warning', 'compliant')

    Returns:
        Emoji string
    """
    emojis = {"critical": "🔴", "warning": "🟠", "compliant": "🟢", "unknown": "⚪"}
    return emojis.get(status, "⚪")


def format_employee_table(employees: list[Any]) -> str:
    """
    Format employees as a table.

    Args:
        employees: List of Employee objects

    Returns:
        Formatted table string
    """
    from employee import calculations

    headers = ["ID WMS", "Nom", "Zone", "Poste", "Contrat", "Statut", "Compliance"]
    rows = []

    for emp in employees:
        compliance_status = calculations.get_compliance_status(emp)
        emoji = get_compliance_emoji(compliance_status)

        rows.append(
            [
                emp.external_id,
                emp.full_name,
                emp.workspace or "",
                emp.role or "",
                emp.contract_type or "",
                "Actif" if emp.is_active else "Inactif",
                f"{emoji} {compliance_status.capitalize()}",
            ]
        )

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_employee_detail(employee: Any) -> str:
    """
    Format detailed employee information.

    Args:
        employee: Employee object

    Returns:
        Formatted detail string
    """
    from employee import calculations

    lines = [
        f"ID WMS:        {employee.external_id}",
        f"Nom:           {employee.full_name}",
        f"Zone:          {employee.workspace or 'N/A'}",
        f"Poste:         {employee.role or 'N/A'}",
        f"Contrat:       {employee.contract_type or 'N/A'}",
        f"Date entrée:   {employee.entry_date or 'N/A'}",
        f"Statut:        {'Actif' if employee.is_active else 'Inactif'}",
    ]

    # Add compliance info
    compliance_status = calculations.get_compliance_status(employee)
    score_data = calculations.calculate_compliance_score(employee)
    emoji = get_compliance_emoji(compliance_status)

    lines.extend(
        [
            "",
            f"Compliance:    {emoji} {compliance_status.capitalize()} ({score_data['score']}/100)",
            f"  - Items valides:    {score_data['valid_items']}",
            f"  - Items critiques:  {score_data['critical_items']}",
            f"  - Items expirés:    {score_data['expired_items']}",
        ]
    )

    return "\n".join(lines)


def format_caces_table(caces_list: list[Any]) -> str:
    """
    Format CACES certifications as a table.

    Args:
        caces_list: List of Caces objects

    Returns:
        Formatted table string
    """
    headers = ["Type", "Obtention", "Expiration", "Jours rest.", "Statut"]
    rows = []

    for caces in caces_list:
        if caces.is_expired:
            status = "🔴 Expiré"
        elif caces.status == "critical":
            status = "🟠 Critique"
        else:
            status = "🟢 Valide"

        rows.append([caces.kind, caces.completion_date, caces.expiration_date, caces.days_until_expiration, status])

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_medical_table(visits: list[Any]) -> str:
    """
    Format medical visits as a table.

    Args:
        visits: List of MedicalVisit objects

    Returns:
        Formatted table string
    """
    headers = ["Type", "Date", "Expiration", "Jours rest.", "Résultat", "Statut"]
    rows = []

    for visit in visits:
        if visit.is_expired:
            status = "🔴 Expirée"
        elif visit.days_until_expiration < 30:
            status = "🟠 Critique"
        else:
            status = "🟢 Valide"

        result_emoji = "✅" if visit.result == "fit" else "❌" if visit.result == "unfit" else "⚠️"

        rows.append(
            [
                visit.visit_type,
                visit.visit_date,
                visit.expiration_date,
                visit.days_until_expiration,
                f"{result_emoji} {visit.result}",
                status,
            ]
        )

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_training_table(trainings: list[Any]) -> str:
    """
    Format online trainings as a table.

    Args:
        trainings: List of OnlineTraining objects

    Returns:
        Formatted table string
    """
    headers = ["Titre", "Complétion", "Expiration", "Jours rest.", "Statut"]
    rows = []

    for training in trainings:
        if not training.expires:
            status = "🟢 Permanent"
            expiration = "N/A"
            days = "-"
        elif training.is_expired:
            status = "🔴 Expirée"
            expiration = training.expiration_date
            days = training.days_until_expiration
        elif training.days_until_expiration < 30:
            status = "🟠 Critique"
            expiration = training.expiration_date
            days = training.days_until_expiration
        else:
            status = "🟢 Valide"
            expiration = training.expiration_date
            days = training.days_until_expiration

        rows.append([training.title, training.completion_date, expiration, days, status])

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_dashboard(stats: dict[str, Any]) -> str:
    """
    Format dashboard statistics.

    Args:
        stats: Dictionary with statistics

    Returns:
        Formatted dashboard string
    """
    from datetime import datetime

    lines = [
        "┌──────────────────────────────────────────────────────┐",
        "│            📊 Tableau de Bord                        │",
        "├──────────────────────────────────────────────────────┤",
        "",
        "  📈 Effectif",
        f"  ├─ Employés total:        {stats.get('total_employees', 0)}",
        f"  ├─ Employés actifs:       {stats.get('active_employees', 0)}",
        f"  └─ Employés inactifs:     {stats.get('total_employees', 0) - stats.get('active_employees', 0)}",
        "",
        "  🚨 Conformité",
        f"  ├─ CACES expirés:         {stats.get('expired_caces', 0)}",
        f"  ├─ CACES critiques:       {stats.get('critical_caces', 0)}",
        f"  ├─ Visites expirées:      {stats.get('expired_visits', 0)}",
        f"  ├─ Visites critiques:     {stats.get('critical_visits', 0)}",
        f"  ├─ Formations expirées:   {stats.get('expired_trainings', 0)}",
        f"  └─ Formations critiques:  {stats.get('critical_trainings', 0)}",
        "",
        "  👷 Employés inaptes:       " + str(stats.get("unfit_count", 0)),
        "",
        f"🕒 Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "└──────────────────────────────────────────────────────┘",
    ]

    return "\n".join(lines)


def format_alerts(employees: list[Any], critical_days: int = 7, warning_days: int = 30) -> str:
    """
    Format alerts for expiring items.

    Args:
        employees: List of employees
        critical_days: Days threshold for critical alerts
        warning_days: Days threshold for warning alerts

    Returns:
        Formatted alerts string
    """
    from employee import calculations

    critical_items = []
    warning_items = []

    for emp in employees:
        # Check CACES
        for caces in emp.caces:
            if caces.is_expired:
                critical_items.append(
                    {
                        "employee": emp,
                        "type": "CACES",
                        "description": f"{caces.kind} expiré depuis {abs(caces.days_until_expiration)} jours",
                    }
                )
            elif caces.days_until_expiration < critical_days:
                critical_items.append(
                    {
                        "employee": emp,
                        "type": "CACES",
                        "description": f"{caces.kind} expire dans {caces.days_until_expiration} jours",
                    }
                )
            elif caces.days_until_expiration < warning_days:
                warning_items.append(
                    {
                        "employee": emp,
                        "type": "CACES",
                        "description": f"{caces.kind} expire dans {caces.days_until_expiration} jours",
                    }
                )

        # Check medical visits
        for visit in emp.medical_visits:
            if visit.is_expired:
                critical_items.append(
                    {
                        "employee": emp,
                        "type": "Visite médicale",
                        "description": f"expirée depuis {abs(visit.days_until_expiration)} jours",
                    }
                )
            elif visit.days_until_expiration < critical_days:
                critical_items.append(
                    {
                        "employee": emp,
                        "type": "Visite médicale",
                        "description": f"expire dans {visit.days_until_expiration} jours",
                    }
                )
            elif visit.days_until_expiration < warning_days:
                warning_items.append(
                    {
                        "employee": emp,
                        "type": "Visite médicale",
                        "description": f"expire dans {visit.days_until_expiration} jours",
                    }
                )

        # Check trainings
        for training in emp.trainings:
            if training.expires:
                if training.is_expired:
                    critical_items.append(
                        {
                            "employee": emp,
                            "type": "Formation",
                            "description": f'"{training.title}" expirée depuis {abs(training.days_until_expiration)} jours',
                        }
                    )
                elif training.days_until_expiration < critical_days:
                    critical_items.append(
                        {
                            "employee": emp,
                            "type": "Formation",
                            "description": f'"{training.title}" expire dans {training.days_until_expiration} jours',
                        }
                    )
                elif training.days_until_expiration < warning_days:
                    warning_items.append(
                        {
                            "employee": emp,
                            "type": "Formation",
                            "description": f'"{training.title}" expire dans {training.days_until_expiration} jours',
                        }
                    )

    # Build output
    lines = [
        f"┌─────────────────────────────────────────────────────────┐",
        f"│  🔔 ALERTES - Items expirant dans les {warning_days} prochains jours│",
        f"├─────────────────────────────────────────────────────────┤",
    ]

    if critical_items:
        lines.append(f"│  🔴 CRITIQUES (< {critical_days} jours)                              │")
        lines.append("│                                                              │")

        for item in critical_items[:10]:  # Limit to 10 items
            emp = item["employee"]
            lines.append(f"│  ├─ {emp.external_id}: {item['type']} {item['description']}")
            lines.append(f"│  │   ├─ Employé: {emp.full_name}")
            lines.append(f"│  │   └─ Poste: {emp.role or 'N/A'}")

        if len(critical_items) > 10:
            lines.append(f"│  └─ ... et {len(critical_items) - 10} autres")

    if warning_items:
        if critical_items:
            lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append(f"│  🟠 ATTENTION (< {warning_days} jours)                             │")
        lines.append("│                                                              │")

        for item in warning_items[:10]:  # Limit to 10 items
            emp = item["employee"]
            lines.append(f"│  ├─ {emp.external_id}: {item['type']} {item['description']}")
            lines.append(f"│  │   ├─ Employé: {emp.full_name}")
            lines.append(f"│  │   └─ Poste: {emp.role or 'N/A'}")

        if len(warning_items) > 10:
            lines.append(f"│  └─ ... et {len(warning_items) - 10} autres")

    lines.append("└─────────────────────────────────────────────────────────┘")

    if not critical_items and not warning_items:
        return "\n".join(
            [
                "┌─────────────────────────────────────────────────────────┐",
                "│  ✅ Aucune alerte - Tous les items sont à jour           │",
                "└─────────────────────────────────────────────────────────┘",
            ]
        )

    lines.append(f"\nTotal: {len(critical_items)} critiques, {len(warning_items)} attentions")

    return "\n".join(lines)
