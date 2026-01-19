"""App shell layout with persistent navigation.

Provides the main application layout with AppBar, navigation,
and content area that changes based on routing.
"""

import flet as ft
from ui.constants import Spacing, MAX_CONTENT_WIDTH, NAVBAR_HEIGHT
from ui.theme import AppTheme
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors, get_primary_color


class AppShell(ft.Column):
    """
    Main application layout shell.

    Provides persistent AppBar and navigation with dynamic content area.
    Eliminates the need for page.clean() by using a container that updates.

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

        # Navigation bar
        self.nav_bar = self._build_navigation()

        # App bar
        self.app_bar = ft.AppBar(
            title=ft.Text(
                "Employee Manager",
                size=20,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=self._colors["surface"],
            elevation=1,
            actions=self._build_app_bar_actions(),
        )

        # Initialize router with content container
        router = get_router(page)
        router.set_content_container(self.content_container)
        router.set_app_bar(self.app_bar)

        # Build shell layout
        super().__init__(
            [
                self.app_bar,
                ft.Container(
                    content=ft.Column(
                        [
                            self.nav_bar,
                            ft.Container(
                                content=self.content_container,
                                width=MAX_CONTENT_WIDTH,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=ft.alignment.Alignment(0, 0),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

    def _build_navigation(self) -> ft.Container:
        """Build the navigation bar."""
        from ui.components.buttons import AppButton
        from ui.components.icons import Icons, IconSize

        return ft.Container(
            content=ft.Row(
                [
                    self._nav_button(
                        "Dashboard",
                        Icons.HOME,
                        "/",
                    ),
                    ft.Container(width=Spacing.SM.value),
                    self._nav_button(
                        "Employees",
                        Icons.PEOPLE,
                        "/employees",
                    ),
                    ft.Container(width=Spacing.SM.value),
                    self._nav_button(
                        "Alerts",
                        Icons.WARNING,
                        "/alerts",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(
                horizontal=Spacing.MD.value,
                vertical=Spacing.SM.value
            ),
            bgcolor=self._colors["surface_variant"],
        )

    def _nav_button(
        self,
        label: str,
        icon: str,
        route: str
    ) -> ft.Container:
        """Build a navigation button."""
        from ui.components.icons import AppIcon, IconSize

        is_active = (self._current_route == route)

        # Style based on active state
        if is_active:
            bgcolor = get_primary_color()
            text_color = ft.Colors.WHITE
            icon_color = ft.Colors.WHITE
        else:
            bgcolor = ft.Colors.TRANSPARENT
            text_color = self._colors["on_surface_variant"]
            icon_color = self._colors["on_surface_variant"]

        button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        icon,
                        size=IconSize.SM.value,
                        color=icon_color,
                    ),
                    ft.Container(width=Spacing.XS.value),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                        color=text_color,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=bgcolor,
            padding=ft.padding.symmetric(
                horizontal=Spacing.MD.value,
                vertical=Spacing.SM.value
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

        # Update navigation visuals
        self._current_route = route
        self.nav_bar.content = self._build_navigation().content
        self.nav_bar.update()

    def _build_app_bar_actions(self) -> list:
        """Build app bar action buttons."""
        from ui.components.icons import Icons

        return [
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
        ]

    def _toggle_theme(self, e):
        """Toggle between light and dark theme."""
        from ui.state.app_state import get_app_state

        app_state = get_app_state()
        app_state.toggle_theme()

        # Update page theme mode
        self._page.theme_mode = app_state.get_flet_theme_mode()
        self._page.update()
