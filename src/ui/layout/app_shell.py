"""App shell layout with persistent navigation.

Provides the main application layout with AppBar, navigation,
and content area that changes based on routing.
"""

import flet as ft
from ui.constants import Spacing, MAX_CONTENT_WIDTH, NAVBAR_HEIGHT
from ui.theme import AppTheme
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors, get_primary_color
from ui.components.icons import Icons


class AppShell(ft.Column):
    """
    Main application layout shell.

    Provides persistent AppBar with integrated navigation and dynamic content area.
    Eliminates the need for page.clean() by using a container that updates.

    Layout: [Title] [Navigation Center] [Actions]

    Args:
        page: The Flet page instance
        current_route: Initial route
    """

    def __init__(self, page: ft.Page, current_route: str = "/"):
        self._page = page
        self._current_route = current_route

        # Get theme colors
        self._colors = get_theme_colors(page)

        # Content container (dynamic content goes here)
        self.content_container = ft.Container(
            content=ft.Container(),
            expand=True,
        )

        # App bar with full custom layout
        self.app_bar = ft.AppBar(
            bgcolor=self._colors["surface"],
            elevation=1,
            toolbar_height=64,
        )

        # Build complete app bar layout with title, center nav, and right actions
        self.app_bar.title = ft.Row(
            [
                # Left side - Title
                ft.Text(
                    "Employee Manager",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    color=self._colors["on_surface"],
                ),

                # Spacer to push nav to center
                ft.Container(expand=True),

                # Center - Navigation
                ft.Row(
                    [
                        self._nav_button(
                            "Dashboard",
                            Icons.HOME,
                            "/",
                        ),
                        ft.Container(width=Spacing.XS.value),
                        self._nav_button(
                            "Employees",
                            Icons.PEOPLE,
                            "/employees",
                        ),
                        ft.Container(width=Spacing.XS.value),
                        self._nav_button(
                            "Alerts",
                            Icons.WARNING,
                            "/alerts",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # Spacer for balance
                ft.Container(expand=True),

                # Right side - Actions
                ft.IconButton(
                    icon=Icons.SETTINGS,
                    tooltip="Settings",
                    on_click=lambda e: self._navigate("/settings"),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.LIGHT_MODE,
                    tooltip="Toggle theme",
                    on_click=self._toggle_theme,
                ),
            ],
            expand=True,
        )

        self.app_bar.center_title = False
        self.app_bar.actions = []

        # Initialize router with content container
        router = get_router(page)
        router.set_content_container(self.content_container)
        router.set_app_bar(self.app_bar)

        # Build shell layout
        super().__init__(
            [
                self.app_bar,
                ft.Container(
                    content=self.content_container,
                    width=MAX_CONTENT_WIDTH,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

    def _nav_button(
        self,
        label: str,
        icon: str,
        route: str
    ) -> ft.Container:
        """Build a navigation button."""
        is_active = (self._current_route == route)

        # Style based on active state
        if is_active:
            bgcolor = get_primary_color()
            text_color = ft.Colors.WHITE
        else:
            bgcolor = ft.Colors.TRANSPARENT
            text_color = self._colors["on_surface_variant"]

        button = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                        color=text_color,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=bgcolor,
            padding=ft.padding.symmetric(
                horizontal=Spacing.SM.value,
                vertical=Spacing.XS.value
            ),
            border_radius=8,
            on_click=lambda e: self._navigate(route),
        )

        return button

    def _navigate(self, route: str):
        """Navigate to route."""
        from ui.navigation.router import get_router

        router = get_router(self._page)
        router.navigate(route)

        # Update navigation visuals by rebuilding app bar
        self._current_route = route
        self.app_bar.title = ft.Row(
            [
                # Left side - Title
                ft.Text(
                    "Employee Manager",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    color=self._colors["on_surface"],
                ),

                # Spacer to push nav to center
                ft.Container(expand=True),

                # Center - Navigation
                ft.Row(
                    [
                        self._nav_button(
                            "Dashboard",
                            Icons.HOME,
                            "/",
                        ),
                        ft.Container(width=Spacing.XS.value),
                        self._nav_button(
                            "Employees",
                            Icons.PEOPLE,
                            "/employees",
                        ),
                        ft.Container(width=Spacing.XS.value),
                        self._nav_button(
                            "Alerts",
                            Icons.WARNING,
                            "/alerts",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # Spacer for balance
                ft.Container(expand=True),

                # Right side - Actions
                ft.IconButton(
                    icon=Icons.SETTINGS,
                    tooltip="Settings",
                    on_click=lambda e: self._navigate("/settings"),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.LIGHT_MODE,
                    tooltip="Toggle theme",
                    on_click=self._toggle_theme,
                ),
            ],
            expand=True,
        )
        self.app_bar.update()

    def _toggle_theme(self, e):
        """Toggle between light and dark theme."""
        from ui.state.app_state import get_app_state

        app_state = get_app_state()
        app_state.toggle_theme()

        # Update page theme mode
        self._page.theme_mode = app_state.get_flet_theme_mode()
        self._page.update()
