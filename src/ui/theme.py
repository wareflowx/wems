"""Theme system for consistent UI styling.

Provides centralized theme management with light and dark mode support.
Uses Material Design 3 principles with custom color schemes.
"""

import flet as ft
from ui.constants import Spacing, BorderRadius


class AppTheme:
    """Centralized theme management for the application."""

    # Color palette - semantic colors
    PRIMARY = ft.Colors.BLUE
    PRIMARY_VARIANT = ft.Colors.BLUE_700
    SECONDARY = ft.Colors.AMBER
    SECONDARY_VARIANT = ft.Colors.AMBER_700

    # Semantic colors
    SUCCESS = ft.Colors.GREEN
    SUCCESS_LIGHT = ft.Colors.GREEN_100
    SUCCESS_DARK = ft.Colors.GREEN_700

    WARNING = ft.Colors.ORANGE
    WARNING_LIGHT = ft.Colors.ORANGE_100
    WARNING_DARK = ft.Colors.ORANGE_700

    ERROR = ft.Colors.RED
    ERROR_LIGHT = ft.Colors.RED_100
    ERROR_DARK = ft.Colors.RED_700

    INFO = ft.Colors.CYAN
    INFO_LIGHT = ft.Colors.CYAN_100
    INFO_DARK = ft.Colors.CYAN_700

    # Neutral colors
    SURFACE = ft.Colors.WHITE
    SURFACE_VARIANT = ft.Colors.GREY_100
    BACKGROUND = ft.Colors.GREY_50

    # Text colors
    ON_SURFACE = ft.Colors.GREY_900
    ON_SURFACE_VARIANT = ft.Colors.GREY_700
    ON_BACKGROUND = ft.Colors.GREY_900
    DISABLED = ft.Colors.GREY_400

    @classmethod
    def get_light_theme(cls) -> ft.Theme:
        """
        Get the light theme configuration.

        Returns:
            ft.Theme configured for light mode
        """
        return ft.Theme(
            color_scheme_seed=cls.PRIMARY,
            theme_mode=ft.ThemeMode.LIGHT,
            # Typography
            text_theme=ft.TextTheme(
                display_large=ft.TextStyle(
                    font_size=57,
                    weight=ft.FontWeight.W_400,
                ),
                headline_medium=ft.TextStyle(
                    font_size=28,
                    weight=ft.FontWeight.W_400,
                ),
                title_large=ft.TextStyle(
                    font_size=22,
                    weight=ft.FontWeight.W_500,
                ),
                body_large=ft.TextStyle(
                    font_size=16,
                    weight=ft.FontWeight.W_400,
                ),
                body_medium=ft.TextStyle(
                    font_size=14,
                    weight=ft.FontWeight.W_400,
                ),
            ),
            # Button themes
            elevated_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            outlined_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            text_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            # Card theme
            card_theme=ft.CardTheme(
                elevation=2,
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG.value),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            # TextField theme
            text_field_theme=ft.TextFieldTheme(
                fill_color=ft.Colors.GREY_50,
                cursor_color=cls.PRIMARY,
                focused_color=ft.Colors.with_opacity(0.1, cls.PRIMARY),
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
            ),
            # Chip theme
            chip_theme=ft.ChipTheme(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.SM.value,
                    vertical=Spacing.XS.value
                ),
            ),
            # Dialog theme
            dialog_theme=ft.DialogTheme(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG.value),
            ),
        )

    @classmethod
    def get_dark_theme(cls) -> ft.Theme:
        """
        Get the dark theme configuration.

        Returns:
            ft.Theme configured for dark mode
        """
        return ft.Theme(
            color_scheme_seed=cls.PRIMARY,
            theme_mode=ft.ThemeMode.DARK,
            # Typography (same as light)
            text_theme=ft.TextTheme(
                display_large=ft.TextStyle(
                    font_size=57,
                    weight=ft.FontWeight.W_400,
                ),
                headline_medium=ft.TextStyle(
                    font_size=28,
                    weight=ft.FontWeight.W_400,
                ),
                title_large=ft.TextStyle(
                    font_size=22,
                    weight=ft.FontWeight.W_500,
                ),
                body_large=ft.TextStyle(
                    font_size=16,
                    weight=ft.FontWeight.W_400,
                ),
                body_medium=ft.TextStyle(
                    font_size=14,
                    weight=ft.FontWeight.W_400,
                ),
            ),
            # Button themes (same shape, different colors auto-applied)
            elevated_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            outlined_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            text_button_theme=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.MD.value,
                    vertical=Spacing.SM.value
                ),
            ),
            # Card theme
            card_theme=ft.CardTheme(
                elevation=2,
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG.value),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            # TextField theme (dark background)
            text_field_theme=ft.TextFieldTheme(
                fill_color=ft.Colors.GREY_800,
                cursor_color=cls.PRIMARY,
                focused_color=ft.Colors.with_opacity(0.1, cls.PRIMARY),
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
            ),
            # Chip theme
            chip_theme=ft.ChipTheme(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM.value),
                padding=ft.padding.symmetric(
                    horizontal=Spacing.SM.value,
                    vertical=Spacing.XS.value
                ),
            ),
            # Dialog theme
            dialog_theme=ft.DialogTheme(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG.value),
            ),
        )

    @classmethod
    def get_button_style(cls, variant: str = "primary") -> ft.ButtonStyle:
        """
        Get button style for different variants.

        Args:
            variant: Button variant - 'primary', 'secondary', 'success',
                    'warning', 'error', 'outline'

        Returns:
            ft.ButtonStyle configured for the variant
        """
        styles = {
            "primary": ft.ButtonStyle(
                bgcolor=cls.PRIMARY,
                color=ft.Colors.WHITE,
            ),
            "secondary": ft.ButtonStyle(
                bgcolor=cls.SECONDARY,
                color=ft.Colors.BLACK,
            ),
            "success": ft.ButtonStyle(
                bgcolor=cls.SUCCESS,
                color=ft.Colors.WHITE,
            ),
            "warning": ft.ButtonStyle(
                bgcolor=cls.WARNING,
                color=ft.Colors.BLACK,
            ),
            "error": ft.ButtonStyle(
                bgcolor=cls.ERROR,
                color=ft.Colors.WHITE,
            ),
            "outline": ft.ButtonStyle(
                bgcolor=ft.Colors.TRANSPARENT,
                color=cls.PRIMARY,
            ),
        }
        return styles.get(variant, styles["primary"])

    @classmethod
    def get_card_style(cls) -> dict:
        """
        Get common card styling properties.

        Returns:
            Dictionary with card styling properties
        """
        return {
            "bgcolor": cls.SURFACE,
            "border_radius": BorderRadius.LG.value,
            "padding": Spacing.MD.value,
        }

    @classmethod
    def get_input_style(cls) -> dict:
        """
        Get common input field styling properties.

        Returns:
            Dictionary with input styling properties
        """
        return {
            "border_radius": BorderRadius.MD.value,
            "filled": True,
        }
