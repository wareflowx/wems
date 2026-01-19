"""Theme-aware color helpers for consistent theming.

Provides functions to get colors that adapt to the current theme mode.
These helpers automatically return appropriate colors for light/dark mode.
"""

import flet as ft


def get_theme_colors(page: ft.Page) -> dict:
    """
    Get theme-aware colors based on current page theme.

    Args:
        page: The Flet page instance

    Returns:
        Dictionary of theme-aware colors
    """
    # Determine if dark mode
    is_dark = page.theme_mode == ft.ThemeMode.DARK

    if is_dark:
        return {
            "surface": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            "surface_variant": ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            "background": ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
            "on_surface": ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
            "on_surface_variant": ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
            "outline": ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            "outline_variant": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "shadow": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            "inactve_surface": ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            "error_container": ft.Colors.with_opacity(0.15, ft.Colors.RED),
        }
    else:
        return {
            "surface": ft.Colors.WHITE,
            "surface_variant": ft.Colors.GREY_100,
            "background": ft.Colors.GREY_50,
            "on_surface": ft.Colors.GREY_900,
            "on_surface_variant": ft.Colors.GREY_700,
            "outline": ft.Colors.GREY_300,
            "outline_variant": ft.Colors.GREY_200,
            "shadow": ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            "inactve_surface": ft.Colors.GREY_100,
            "error_container": ft.Colors.with_opacity(0.1, ft.Colors.RED),
        }


def get_card_color(page: ft.Page) -> str:
    """Get theme-aware card background color."""
    return get_theme_colors(page)["surface"]


def get_background_color(page: ft.Page) -> str:
    """Get theme-aware background color."""
    return get_theme_colors(page)["background"]


def get_navbar_color(page: ft.Page) -> str:
    """Get theme-aware navbar background color."""
    return get_theme_colors(page)["surface_variant"]


def get_text_color(page: ft.Page) -> str:
    """Get theme-aware primary text color."""
    return get_theme_colors(page)["on_surface"]


def get_secondary_text_color(page: ft.Page) -> str:
    """Get theme-aware secondary text color."""
    return get_theme_colors(page)["on_surface_variant"]


def get_outline_color(page: ft.Page) -> str:
    """Get theme-aware outline/border color."""
    return get_theme_colors(page)["outline"]


def get_inactive_bg_color(page: ft.Page) -> str:
    """Get theme-aware inactive/disabled background color."""
    return get_theme_colors(page)["inactve_surface"]


def get_shadow_color(page: ft.Page) -> str:
    """Get theme-aware shadow color."""
    return get_theme_colors(page)["shadow"]


# Semantic colors that work in both light and dark mode
def get_primary_color() -> str:
    """Get primary brand color."""
    return ft.Colors.BLUE


def get_success_color() -> str:
    """Get success color."""
    return ft.Colors.GREEN


def get_warning_color() -> str:
    """Get warning color."""
    return ft.Colors.ORANGE


def get_error_color() -> str:
    """Get error color."""
    return ft.Colors.RED


def get_info_color() -> str:
    """Get info color."""
    return ft.Colors.CYAN
