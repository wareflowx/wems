"""Dashboard view - Main dashboard with statistics and alerts."""

import flet as ft
from typing import List

from ui.controllers.dashboard_controller import DashboardController
from ui.widgets.stat_card import StatCard
from ui.widgets.alert_item import AlertListItem
from ui.widgets.navigation import NavigationBar


class DashboardView:
    """
    Dashboard view builder.

    Constructs the complete dashboard interface with statistics,
    alerts, and action buttons.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize dashboard view.

        Args:
            page: The Flet page instance
        """
        self.page = page
        self.controller = DashboardController()

    def build(self) -> ft.Column:
        """
        Build the dashboard view.

        Returns:
            ft.Column containing all dashboard components
        """
        # Get data
        stats = self.controller.get_statistics()
        compliance = self.controller.get_compliance_percentage()
        total_alerts = self.controller.get_total_alerts_count()
        alerts = self.controller.format_alerts_for_ui(days=30, limit=10)

        # Build components
        nav_bar = NavigationBar(self.page, current_view="dashboard")
        stats_row = self._build_stats_cards(stats, compliance, total_alerts)
        alerts_section = self._build_alerts_section(alerts, total_alerts)
        actions_row = self._build_actions()

        # Assemble dashboard
        dashboard_content = ft.Column(
            [
                ft.Container(height=20),
                stats_row,
                ft.Container(height=20),
                alerts_section,
                ft.Container(height=20),
                actions_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Column(
            [
                nav_bar,
                dashboard_content,
            ],
        )

    def _build_stats_cards(self, stats: dict, compliance: int, total_alerts: int) -> ft.Row:
        """Build the statistics cards row."""
        return ft.Row(
            [
                StatCard(
                    "Total Employees",
                    stats['total_employees'],
                    "👥",
                    ft.Colors.BLUE
                ),
                StatCard(
                    "Active",
                    stats['active_employees'],
                    "✅",
                    ft.Colors.GREEN
                ),
                StatCard(
                    "Alerts",
                    total_alerts,
                    "⚠️",
                    ft.Colors.ORANGE
                ),
                StatCard(
                    "Compliance",
                    f"{compliance}%",
                    "📊",
                    ft.Colors.GREEN if compliance >= 90 else ft.Colors.ORANGE
                ),
            ],
            spacing=10,
            wrap=True,
        )

    def _build_alerts_section(self, alerts: List[dict], total_count: int) -> ft.Column:
        """Build the alerts section."""
        alert_items = []

        if not alerts:
            # No alerts message
            alert_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "✅",
                                size=48,
                            ),
                            ft.Text(
                                "No alerts at the moment!",
                                size=16,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "All certifications are up to date.",
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30,
                )
            )
        else:
            # Build alert list items
            for alert in alerts:
                # Create click handler for navigation
                def navigate_to_employee(e, emp_id=alert['employee_id']):
                    # Navigate to employee detail
                    self.page.clean()
                    from ui.views.employee_detail import EmployeeDetailView
                    detail_view = EmployeeDetailView(self.page, emp_id)
                    self.page.add(
                        ft.AppBar(title=ft.Text("Employee Manager")),
                        detail_view.build(),
                    )
                    self.page.update()

                alert_items.append(
                    AlertListItem(
                        employee_name=alert['employee_name'],
                        description=alert['description'],
                        days_until=alert['days_until'],
                        priority=alert['priority'],
                        on_click=navigate_to_employee,
                    )
                )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Recent Alerts",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"({total_count} total)",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(alert_items, scroll=ft.ScrollMode.AUTO),
            ],
            spacing=10,
        )

    def _build_actions(self) -> ft.Row:
        """Build quick action buttons."""
        def navigate_to_employees(e):
            """Navigate to employees list."""
            self.page.clean()
            from ui.views.employees import EmployeesListView
            employees_view = EmployeesListView(self.page)
            self.page.add(
                ft.AppBar(title=ft.Text("Employee Manager")),
                employees_view.build(),
            )
            self.page.update()

        def navigate_to_alerts(e):
            """Navigate to alerts view."""
            self.page.clean()
            from ui.views.alerts import AlertsView
            alerts_view = AlertsView(self.page)
            self.page.add(
                ft.AppBar(title=ft.Text("Employee Manager")),
                alerts_view.build(),
            )
            self.page.update()

        def navigate_to_add_employee(e):
            """Navigate to add employee form."""
            self.page.clean()
            from ui.views.employee_form import EmployeeFormView
            form_view = EmployeeFormView(self.page, employee_id=None)
            self.page.add(
                ft.AppBar(title=ft.Text("Employee Manager")),
                form_view.build(),
            )
            self.page.update()

        return ft.Row(
            [
                ft.ElevatedButton(
                    "➕ Add Employee",
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=navigate_to_add_employee,
                ),
                ft.ElevatedButton(
                    "👥 View All Employees",
                    on_click=navigate_to_employees,
                ),
                ft.ElevatedButton(
                    "⚠️ View All Alerts",
                    on_click=navigate_to_alerts,
                ),
                ft.ElevatedButton(
                    "📥 Export Report",
                ),
            ],
            spacing=10,
        )
