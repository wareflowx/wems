"""Navigation bar - Persistent navigation across all views."""

import flet as ft
from typing import Callable


class NavigationBar(ft.Container):
    """
    A persistent navigation bar with buttons to main views.

    Provides quick access to Dashboard, Employees, Alerts from any view.

    Args:
        page: The Flet page instance
        current_view: Current view name ('dashboard', 'employees', 'alerts', etc.)
    """

    def __init__(self, page: ft.Page, current_view: str = "dashboard"):
        self._page = page
        self.current_view = current_view

        # Build navigation buttons
        nav_buttons = self._build_nav_buttons()

        super().__init__(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.TextButton(
                            "🏠 Dashboard",
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE if current_view == "dashboard" else None,
                            ),
                            on_click=lambda e: self._navigate_to_dashboard(),
                        ),
                        bgcolor=ft.Colors.BLUE if current_view == "dashboard" else None,
                        border_radius=8,
                        padding=5,
                    ),
                    ft.Container(width=10),
                    ft.Container(
                        content=ft.TextButton(
                            "👥 Employees",
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE if current_view == "employees" else None,
                            ),
                            on_click=lambda e: self._navigate_to_employees(),
                        ),
                        bgcolor=ft.Colors.BLUE if current_view == "employees" else None,
                        border_radius=8,
                        padding=5,
                    ),
                    ft.Container(width=10),
                    ft.Container(
                        content=ft.TextButton(
                            "⚠️ Alerts",
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE if current_view == "alerts" else None,
                            ),
                            on_click=lambda e: self._navigate_to_alerts(),
                        ),
                        bgcolor=ft.Colors.BLUE if current_view == "alerts" else None,
                        border_radius=8,
                        padding=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_200,
            width=800,
        )

    def _build_nav_buttons(self) -> ft.Row:
        """Build navigation buttons row."""
        pass  # Not used anymore

    def _navigate_to_dashboard(self):
        """Navigate to dashboard view."""
        self._page.clean()
        from ui.views.dashboard import DashboardView
        dashboard = DashboardView(self._page)
        self._page.add(
            self._build_app_bar(),
            dashboard.build(),
        )
        self._page.update()

    def _navigate_to_employees(self):
        """Navigate to employees list view."""
        self._page.clean()
        from ui.views.employees import EmployeesListView
        employees_view = EmployeesListView(self._page)
        self._page.add(
            self._build_app_bar(),
            employees_view.build(),
        )
        self._page.update()

    def _navigate_to_alerts(self):
        """Navigate to alerts view."""
        self._page.clean()
        from ui.views.alerts import AlertsView
        alerts_view = AlertsView(self._page)
        self._page.add(
            self._build_app_bar(),
            alerts_view.build(),
        )
        self._page.update()

    def _build_app_bar(self) -> ft.AppBar:
        """Build app bar with title."""
        return ft.AppBar(
            title=ft.Text("Employee Manager"),
            bgcolor=ft.Colors.SURFACE,
        )
