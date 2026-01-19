"""Dashboard view - Main dashboard with statistics and alerts.

Updated to use new professional components and router navigation.
"""

import flet as ft
from typing import List

from ui.controllers.dashboard_controller import DashboardController
from ui.components.cards import StatCard, AppCard
from ui.components.buttons import AppButton, ActionButton
from ui.components.chips import StatusBadge
from ui.components.icons import Icons, IconSize
from ui.components.feedback import show_snackbar
from ui.constants import Spacing
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors, get_primary_color, get_success_color, get_warning_color, get_error_color


class DashboardView:
    """
    Dashboard view builder using professional components.

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
        self._colors = get_theme_colors(page)

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
        dashboard_content = ft.Column(
            [
                ft.Container(height=Spacing.LG.value),
                stats_row,
                ft.Container(height=Spacing.LG.value),
                alerts_section,
                ft.Container(height=Spacing.LG.value),
                actions_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return dashboard_content

    def _build_stats_cards(self, stats: dict, compliance: int, total_alerts: int) -> ft.Row:
        """Build the statistics cards row."""
        return ft.Row(
            [
                StatCard(
                    label="Total Employees",
                    value=stats['total_employees'],
                    icon=Icons.PEOPLE,
                    color=get_primary_color(),
                ),
                StatCard(
                    label="Active",
                    value=stats['active_employees'],
                    icon=Icons.ACTIVE,
                    color=get_success_color(),
                ),
                StatCard(
                    label="Alerts",
                    value=total_alerts,
                    icon=Icons.WARNING,
                    color=get_warning_color(),
                ),
                StatCard(
                    label="Compliance",
                    value=f"{compliance}%",
                    icon=Icons.BADGE,
                    color=get_success_color() if compliance >= 90 else get_warning_color(),
                ),
            ],
            spacing=Spacing.MD.value,
            wrap=True,
        )

    def _build_alerts_section(self, alerts: List[dict], total_count: int) -> AppCard:
        """Build the alerts section."""
        alert_items = []

        if not alerts:
            # No alerts message
            alert_items.append(
                ft.Column(
                    [
                        ft.Icon(
                            Icons.SUCCESS,
                            size=48,
                            color=get_success_color(),
                        ),
                        ft.Container(height=Spacing.SM.value),
                        ft.Text(
                            "No alerts at the moment!",
                            size=16,
                            color=self._colors["on_surface"],
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "All certifications are up to date.",
                            size=12,
                            color=self._colors["on_surface_variant"],
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        else:
            # Build alert list items
            for alert in alerts:
                alert_items.append(
                    self._build_alert_item(alert)
                )

        content = ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Text(
                            "Recent Alerts",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            f"({total_count} total)",
                            size=13,
                            color=self._colors["on_surface_variant"],
                        ),
                    ],
                ),
                ft.Divider(height=1),
                # Alert list
                ft.Column(
                    alert_items,
                    spacing=Spacing.SM.value,
                ),
            ],
            spacing=Spacing.SM.value,
        )

        return AppCard(content=content, padding=Spacing.MD.value)

    def _build_alert_item(self, alert: dict) -> ft.Container:
        """Build a single alert item."""
        # Get priority color
        priority_colors = {
            "high": get_error_color(),
            "medium": get_warning_color(),
            "low": ft.Colors.YELLOW,
        }
        priority_color = priority_colors.get(alert['priority'], ft.Colors.GREY)

        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    Icons.WARNING,
                    color=priority_color,
                ),
                title=ft.Text(
                    alert['employee_name'],
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
                subtitle=ft.Text(
                    alert['description'],
                    size=12,
                    color=self._colors["on_surface_variant"],
                ),
                trailing=ft.Text(
                    f"{alert['days_until']}d",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=priority_color,
                ),
            ),
            bgcolor=self._colors["surface_variant"],
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=Spacing.SM.value, vertical=4),
            on_click=lambda e: self._navigate_to_employee(alert['employee_id']),
            ink=True,
        )

    def _build_actions(self) -> ft.Row:
        """Build quick action buttons."""
        return ft.Row(
            [
                ActionButton(
                    text="Add Employee",
                    icon=Icons.ADD,
                    on_click=lambda e: self._navigate_to_create_employee(),
                    variant="primary",
                ),
                ActionButton(
                    text="View All Employees",
                    icon=Icons.PEOPLE,
                    on_click=lambda e: self._navigate_to_employees(),
                    variant="secondary",
                ),
                ActionButton(
                    text="View All Alerts",
                    icon=Icons.WARNING,
                    on_click=lambda e: self._navigate_to_alerts(),
                    variant="warning",
                ),
                ActionButton(
                    text="Export Report",
                    icon=Icons.EXPORT,
                    on_click=lambda e: self._export_report(),
                    variant="outline",
                ),
            ],
            spacing=Spacing.MD.value,
            wrap=True,
        )

    def _navigate_to_employee(self, employee_id: str):
        """Navigate to employee detail view."""
        router = get_router(self.page)
        router.navigate("/employee", id=employee_id)

    def _navigate_to_employees(self):
        """Navigate to employees list."""
        router = get_router(self.page)
        router.navigate("/employees")

    def _navigate_to_alerts(self):
        """Navigate to alerts view."""
        router = get_router(self.page)
        router.navigate("/alerts")

    def _navigate_to_create_employee(self):
        """Navigate to create employee form."""
        router = get_router(self.page)
        router.navigate("/employee/create")

    def _export_report(self):
        """Export report."""
        show_snackbar(
            self.page,
            "Export feature coming soon!",
            variant="info"
        )
