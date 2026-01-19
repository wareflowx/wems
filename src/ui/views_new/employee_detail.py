"""Employee detail view - Placeholder.

This is a placeholder view that will be fully implemented in Phase 4.
"""

import flet as ft
from ui.constants import Spacing
from ui.components.icons import Icons
from ui.components.buttons import AppButton
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors


class EmployeeDetailView:
    """Employee detail view - placeholder implementation."""

    def __init__(self, page: ft.Page, employee_id: str):
        self.page = page
        self.employee_id = employee_id
        self._colors = get_theme_colors(page)

    def build(self) -> ft.Column:
        """Build employee detail view."""
        content = ft.Column(
            [
                ft.Container(height=Spacing.LG.value),
                ft.Icon(
                    Icons.PERSON,
                    size=64,
                    color=self._colors["on_surface_variant"],
                ),
                ft.Container(height=Spacing.MD.value),
                ft.Text(
                    f"Employee Detail: {self.employee_id}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "This view will be fully implemented in Phase 4",
                    size=14,
                    color=self._colors["on_surface_variant"],
                ),
                ft.Container(height=Spacing.LG.value),
                AppButton(
                    "Back to Employees",
                    variant="secondary",
                    on_click=lambda e: self._go_back(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return content

    def _go_back(self):
        """Navigate back to employees list."""
        router = get_router(self.page)
        router.navigate("/employees")
