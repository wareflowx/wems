"""Dashboard view - Main dashboard with statistics and alerts."""

import flet as ft
from typing import List

from ui.controllers.dashboard_controller import DashboardController
from ui.widgets.stat_card import StatCard
from ui.widgets.alert_item import AlertListItem


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
        stats_row = self._build_stats_cards(stats, compliance, total_alerts)
        alerts_section = self._build_alerts_section(alerts, total_alerts)
        actions_row = self._build_actions()

        # Assemble dashboard
        return ft.Column(
            [
                stats_row,
                ft.Container(height=20),
                alerts_section,
                ft.Container(height=20),
                actions_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
        return ft.Row(
            [
                ft.ElevatedButton(
                    "Add Employee",
                    icon=ft.icons.ADD,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "View All Alerts",
                    icon=ft.icons.ALERTS,
                ),
                ft.ElevatedButton(
                    "Export Report",
                    icon=ft.icons.DOWNLOAD,
                ),
            ],
            spacing=10,
        )
