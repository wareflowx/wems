"""Router for centralized navigation management.

Provides clean navigation without page.clean(), maintains history,
and manages view transitions.
"""

import flet as ft
from typing import Optional, Callable, Dict, Any
from .routes import get_view_builder, Routes


class Router:
    """
    Centralized router for application navigation.

    Manages view transitions, history, and navigation state
    without using page.clean().

    Usage:
        router = Router(page)
        router.navigate(Routes.DASHBOARD)
        router.navigate(Routes.EMPLOYEE_DETAIL, id="123")
        router.go_back()
    """

    def __init__(self, page: ft.Page):
        """
        Initialize router.

        Args:
            page: The Flet page instance
        """
        self.page = page
        self.current_route = Routes.DASHBOARD
        self.history: list = []
        self.params: Dict[str, Any] = {}
        self._content_container: Optional[ft.Container] = None
        self._app_bar: Optional[ft.AppBar] = None

    def navigate(
        self,
        route: str,
        **params
    ):
        """
        Navigate to a route.

        Args:
            route: Route path from Routes class
            **params: Route parameters (e.g., id="123")
        """
        # Save current route to history
        if self.current_route and self.current_route != route:
            self.history.append((self.current_route, self.params.copy()))

        # Update current route
        self.current_route = route
        self.params = params

        # Build and display new view
        self._display_view(route, params)

    def go_back(self):
        """
        Navigate back to previous route in history.

        Returns:
            True if went back, False if no history
        """
        if not self.history:
            return False

        # Pop previous route
        prev_route, prev_params = self.history.pop()
        self.current_route = prev_route
        self.params = prev_params

        # Display view
        self._display_view(prev_route, prev_params)
        return True

    def replace(
        self,
        route: str,
        **params
    ):
        """
        Replace current route (don't add to history).

        Args:
            route: Route path
            **params: Route parameters
        """
        self.current_route = route
        self.params = params
        self._display_view(route, params)

    def set_content_container(self, container: ft.Container):
        """
        Set the main content container for view display.

        Args:
            container: Container that will hold view content
        """
        self._content_container = container

    def set_app_bar(self, app_bar: ft.AppBar):
        """
        Set the app bar.

        Args:
            app_bar: AppBar instance
        """
        self._app_bar = app_bar

    def _display_view(self, route: str, params: Dict[str, Any]):
        """
        Build and display a view.

        Args:
            route: Route path
            params: Route parameters
        """
        # Get view builder
        view_builder = get_view_builder(route)

        if view_builder is None:
            # Show 404
            self._show_not_found(route)
            return

        try:
            # Build view
            view_content = view_builder(self.page, **params)

            # Update content container
            if self._content_container:
                self._content_container.content = view_content
                self._content_container.update()
            else:
                # Fallback: add directly to page (not recommended)
                self.page.clean()
                self.page.add(view_content)

            # Update page route
            self.page.route = route
            self.page.update()

        except Exception as e:
            # Show error
            self._show_error(str(e))

    def _show_not_found(self, route: str):
        """Show 404 not found view."""
        from ui.components.cards import InfoCard

        content = ft.Column(
            [
                ft.Container(height=40),
                ft.Icon(
                    ft.icons.ERROR_OUTLINE,
                    size=64,
                    color=ft.Colors.GREY_400,
                ),
                ft.Container(height=20),
                ft.Text(
                    "Page Not Found",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                ),
                ft.Container(height=10),
                ft.Text(
                    f"The page '{route}' does not exist.",
                    size=14,
                    color=ft.Colors.GREY_500,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        if self._content_container:
            self._content_container.content = content
            self._content_container.update()

    def _show_error(self, error_message: str):
        """Show error view."""
        from ui.components.feedback import show_snackbar

        show_snackbar(
            self.page,
            f"Error loading page: {error_message}",
            variant="error"
        )

    @property
    def can_go_back(self) -> bool:
        """Check if there's history to go back to."""
        return len(self.history) > 0


# Global router instance
_router_instance: Optional[Router] = None


def get_router(page: ft.Page = None) -> Router:
    """
    Get the global router instance.

    Args:
        page: Flet page instance (required on first call)

    Returns:
        Router instance
    """
    global _router_instance

    if _router_instance is None:
        if page is None:
            raise RuntimeError("Router not initialized. Pass page on first call.")
        _router_instance = Router(page)

    return _router_instance


def reset_router():
    """Reset the global router instance (mainly for testing)."""
    global _router_instance
    _router_instance = None
