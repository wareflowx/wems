"""Employee detail view - Displays comprehensive employee information."""

import flet as ft
from typing import Optional

from ui.controllers.employee_controller import EmployeeController


class EmployeeDetailView:
    """
    Employee detail view builder.

    Constructs the complete employee detail interface with
    personal info, compliance score, certifications, and alerts.
    """

    def __init__(self, page: ft.Page, employee_id: str):
        """
        Initialize employee detail view.

        Args:
            page: The Flet page instance
            employee_id: Employee UUID as string
        """
        self.page = page
        self.employee_id = employee_id
        self.controller = EmployeeController()

    def build(self) -> ft.Column:
        """
        Build the employee detail view.

        Returns:
            ft.Column containing all employee detail components
        """
        # Get employee data
        data = self.controller.get_employee_details(self.employee_id)

        if not data:
            return self._build_not_found()

        emp = data['employee']

        # Build components
        header = self._build_header(emp)
        actions_section = self._build_actions_section(self.employee_id)
        info_section = self._build_info_section(emp)
        compliance_section = self._build_compliance_section(data)
        caces_section = self._build_caces_section(data['caces_list'])
        visits_section = self._build_visits_section(data['medical_visits'])
        trainings_section = self._build_trainings_section(data['trainings'])

        # Assemble view
        return ft.Column(
            [
                header,
                ft.Container(height=10),
                actions_section,
                ft.Container(height=20),
                info_section,
                ft.Container(height=20),
                compliance_section,
                ft.Container(height=20),
                caces_section,
                ft.Container(height=20),
                visits_section,
                ft.Container(height=20),
                trainings_section,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_not_found(self) -> ft.Column:
        """Build employee not found message."""
        return ft.Column(
            [
                ft.Icon(
                    ft.icons.ERROR,
                    size=64,
                    color=ft.Colors.RED
                ),
                ft.Text(
                    "Employee Not Found",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED,
                ),
                ft.Text(
                    f"No employee found with ID: {self.employee_id}",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.ElevatedButton(
                    "← Back to Dashboard",
                    on_click=lambda e: self._navigate_to_dashboard(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_header(self, emp) -> ft.Row:
        """Build header with back button and employee name."""
        return ft.Row(
            [
                ft.IconButton(
                    ft.icons.CHEVRON_LEFT,
                    on_click=lambda e: self._navigate_to_dashboard(),
                ),
                ft.Text(
                    emp.full_name,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

    def _build_actions_section(self, employee_id: str) -> ft.Row:
        """Build action buttons for employee."""
        def navigate_to_edit(e):
            """Navigate to edit form."""
            self.page.clean()
            from ui.views.employee_form import EmployeeFormView
            form_view = EmployeeFormView(self.page, employee_id=employee_id)
            self.page.add(
                ft.AppBar(title=ft.Text("Employee Manager")),
                form_view.build(),
            )
            self.page.update()

        return ft.Row(
            [
                ft.ElevatedButton(
                    "✏️ Edit",
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=navigate_to_edit,
                ),
            ],
            spacing=10,
        )

    def _build_info_section(self, emp) -> ft.Container:
        """Build basic employee information section."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Information",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    self._info_row("Status", emp.current_status.capitalize()),
                    self._info_row("Workspace", emp.workspace),
                    self._info_row("Role", emp.role),
                    self._info_row("Contract Type", emp.contract_type),
                    self._info_row("Entry Date", emp.entry_date.strftime("%d/%m/%Y")),
                    self._info_row("Seniority", f"{emp.seniority} years"),
                ],
                spacing=5,
            ),
            width=800,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
        )

    def _build_compliance_section(self, data: dict) -> ft.Container:
        """Build compliance score section."""
        score = data['compliance_score']
        breakdown = data['score_breakdown']

        # Color based on score
        if score >= 70:
            color = ft.Colors.GREEN
            status = "Compliant"
        elif score >= 50:
            color = ft.Colors.ORANGE
            status = "Warning"
        else:
            color = ft.Colors.RED
            status = "Critical"

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Compliance Score",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Text(
                                str(score),
                                size=48,
                                weight=ft.FontWeight.BOLD,
                                color=color,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        status,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=color,
                                    ),
                                    ft.Text(
                                        f"CACES: {breakdown['caces']}/30",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                    ft.Text(
                                        f"Medical: {breakdown['medical']}/30",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                    ft.Text(
                                        f"Training: {breakdown['training']}/40",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
            width=800,
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
        )

    def _build_caces_section(self, caces_list: list) -> ft.Container:
        """Build CACES certifications section."""
        items = []
        for caces in caces_list:
            days = caces.days_until_expiration
            if days < 0:
                status_text = f"Expired {abs(days)} days ago"
                status_color = ft.Colors.RED
            elif days < 30:
                status_text = f"Expires in {days} days"
                status_color = ft.Colors.ORANGE
            else:
                status_text = f"Valid ({days} days remaining)"
                status_color = ft.Colors.GREEN

            items.append(
                ft.ListTile(
                    leading=ft.Text("🏗️", size=24),
                    title=ft.Text(f"CACES {caces.kind}"),
                    subtitle=ft.Text(status_text, color=status_color),
                    trailing=ft.Text(
                        caces.expiration_date.strftime("%d/%m/%Y"),
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                )
            )

        if not items:
            items.append(ft.Text("No CACES certifications", color=ft.Colors.GREY_500))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "CACES Certifications",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Column(items, spacing=5),
                ],
            ),
            width=800,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
        )

    def _build_visits_section(self, visits: list) -> ft.Container:
        """Build medical visits section."""
        items = []
        for visit in visits:
            days = visit.days_until_expiration
            if visit.result == 'unfit':
                status_text = "⛔ Unfit"
                status_color = ft.Colors.RED
            elif days < 0:
                status_text = f"Expired {abs(days)} days ago"
                status_color = ft.Colors.RED
            elif days < 30:
                status_text = f"Expires in {days} days"
                status_color = ft.Colors.ORANGE
            else:
                status_text = f"Valid ({days} days remaining)"
                status_color = ft.Colors.GREEN

            items.append(
                ft.ListTile(
                    leading=ft.Text("🏥", size=24),
                    title=ft.Text(f"{visit.visit_type.capitalize()} Visit"),
                    subtitle=ft.Text(status_text, color=status_color),
                    trailing=ft.Text(
                        visit.visit_date.strftime("%d/%m/%Y"),
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                )
            )

        if not items:
            items.append(ft.Text("No medical visits", color=ft.Colors.GREY_500))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Medical Visits",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Column(items, spacing=5),
                ],
            ),
            width=800,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
        )

    def _build_trainings_section(self, trainings: list) -> ft.Container:
        """Build online trainings section."""
        items = []
        for training in trainings:
            days = training.days_until_expiration
            if days is not None and days < 365:
                status_text = f"Expires in {days} days"
            else:
                status_text = "Valid"

            items.append(
                ft.ListTile(
                    leading=ft.Text("📚", size=24),
                    title=ft.Text(training.title),
                    subtitle=ft.Text(status_text),
                    trailing=ft.Text(
                        training.completed_date.strftime("%d/%m/%Y"),
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                )
            )

        if not items:
            items.append(ft.Text("No online trainings", color=ft.Colors.GREY_500))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Online Trainings",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Column(items, spacing=5),
                ],
            ),
            width=800,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
        )

    def _info_row(self, label: str, value: str) -> ft.Row:
        """Build a row for info section."""
        return ft.Row(
            [
                ft.Text(
                    label,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                    width=150,
                ),
                ft.Text(
                    value,
                    size=14,
                    color=ft.Colors.GREY_900,
                ),
            ],
        )

    def _navigate_to_dashboard(self):
        """Navigate back to dashboard."""
        # Clear page and show dashboard
        self.page.clean()
        from ui.views.dashboard import DashboardView
        dashboard = DashboardView(self.page)
        self.page.add(
            ft.AppBar(title=ft.Text("Employee Manager")),
            dashboard.build(),
        )
        self.page.update()
