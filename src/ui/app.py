"""Flet application entry point."""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import flet as ft
from .state.app_state import get_app_state


def ensure_database():
    """Ensure database is initialized before starting the app."""
    db_path = Path("employee_manager.db")

    # If database doesn't exist, initialize it
    if not db_path.exists():
        from database.connection import init_database
        init_database(db_path)
        print(f"Database initialized: {db_path}")


def route_change(route: str, page: ft.Page, app_state):
    """Handle route changes and build views accordingly."""
    page.views.clear()

    # Common AppBar
    appbar = ft.AppBar(
        title=ft.Text("Employee Manager"),
        bgcolor=ft.Colors.SURFACE,
        actions=[
            ft.Container(
                content=ft.Text(
                    app_state.lock_status,
                    size=12,
                    color=ft.Colors.GREY_700
                ),
                padding=5,
                bgcolor=ft.Colors.GREY_100,
                border_radius=20,
            ),
        ],
    )

    # Dashboard view
    if page.route == "/":
        page.views.append(
            ft.View(
                "/",
                [
                    appbar,
                    ft.Column(
                        [
                            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=16),
                        ],
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # Employees list view
    elif page.route == "/employees":
        page.views.append(
            ft.View(
                "/employees",
                [
                    appbar,
                    ft.Column(
                        [
                            ft.Text("Employees", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=16),
                        ],
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # Employee detail view
    elif page.route.startswith("/employee/"):
        emp_id = page.route.split("/")[-1]
        page.views.append(
            ft.View(
                page.route,
                [
                    appbar,
                    ft.Column(
                        [
                            ft.Text(f"Employee {emp_id}", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=16),
                        ],
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # Documents view
    elif page.route == "/documents":
        page.views.append(
            ft.View(
                "/documents",
                [
                    appbar,
                    ft.Column(
                        [
                            ft.Text("Documents", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=16),
                        ],
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # Settings view
    elif page.route == "/settings":
        page.views.append(
            ft.View(
                "/settings",
                [
                    appbar,
                    ft.Column(
                        [
                            ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=16),
                        ],
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    page.update()


def view_pop(view, page: ft.Page):
    """Handle back navigation."""
    page.views.pop()
    top_view = page.views[-1]
    page.route = top_view.route
    page.update()


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    # Ensure database exists before starting
    ensure_database()

    # Get application state
    app_state = get_app_state()

    # Try to acquire lock
    if not app_state.acquire_lock():
        page.title = "Employee Manager - Lock Error"
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "⛔ Unable to acquire application lock",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED
                        ),
                        ft.Text(app_state.lock_status, size=14),
                        ft.Text("Another instance may be running.", size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            )
        )
        return

    # Configure page
    page.title = "Employee Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    # Set up route change handler
    def on_route_change(route):
        route_change(route, page, app_state)

    page.on_route_change = on_route_change
    page.on_view_pop = view_pop

    # Navigate to initial route - call route change directly
    on_route_change(page.route)


if __name__ == "__main__":
    ft.run(main)
