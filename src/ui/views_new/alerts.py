"""Alerts view - Placeholder.

This is a placeholder view that will be fully implemented in Phase 4.
"""

import flet as ft
from ui.constants import Spacing
from ui.components.icons import Icons
from ui.components.buttons import AppButton
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors


class AlertsView:
    """Alerts view - placeholder implementation."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._colors = get_theme_colors(page)

    def build(self) -> ft.Column:
        """Build alerts view."""
        content = ft.Column(
            [
                ft.Container(height=Spacing.LG.value),
                ft.Icon(
                    Icons.WARNING,
                    size=64,
                    color=self._colors["on_surface_variant"],
                ),
                ft.Container(height=Spacing.MD.value),
                ft.Text(
                    "Alerts View",
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
                    "Back to Dashboard",
                    variant="secondary",
                    on_click=lambda e: self._go_back(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return content

    def _go_back(self):
        """Navigate back to dashboard."""
        router = get_router(self.page)
        router.navigate("/")
