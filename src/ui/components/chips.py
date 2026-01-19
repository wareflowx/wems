"""Chip and badge components with consistent styling.

Provides themed chips for filtering, selection, and status display.
"""

import flet as ft
from ui.constants import Spacing, BorderRadius, IconSize
from ui.theme import AppTheme


class AppChip(ft.Chip):
    """
    A themed chip for filtering and selection.

    Args:
        label: Chip label text
        selected: Whether chip is selected
        on_click: Click handler
        variant: Style variant - 'primary', 'secondary', 'success', 'warning', 'error'
        icon: Optional icon to show
        **kwargs: Additional ft.Chip properties
    """

    def __init__(
        self,
        label: str,
        selected: bool = False,
        on_click=None,
        variant: str = "primary",
        icon: str = None,
        **kwargs
    ):
        # Get variant colors
        variant_colors = {
            "primary": AppTheme.PRIMARY,
            "secondary": AppTheme.SECONDARY,
            "success": AppTheme.SUCCESS,
            "warning": AppTheme.WARNING,
            "error": AppTheme.ERROR,
        }
        self._variant_color = variant_colors.get(variant, AppTheme.PRIMARY)

        # Build label with optional icon
        if icon:
            from ui.components.icons import AppIcon
            label_content = ft.Row(
                [
                    AppIcon(icon, size=IconSize.XS.value, color=self._variant_color),
                    ft.Container(width=Spacing.XS.value),
                    ft.Text(label, size=12),
                ],
                spacing=0,
            )
        else:
            label_content = ft.Text(label, size=12)

        super().__init__(
            label=label_content,
            selected=selected,
            on_click=on_click,
            **kwargs
        )


class AppBadge(ft.Container):
    """
    A badge component for displaying counts and status.

    Args:
        text: Badge text
        count: Optional count number to display
        variant: Style variant - 'primary', 'secondary', 'success', 'warning', 'error'
        size: Badge size - 'sm', 'md', 'lg'
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        text: str,
        count: int = None,
        variant: str = "primary",
        size: str = "md",
        **kwargs
    ):
        # Get variant colors
        variant_colors = {
            "primary": (AppTheme.PRIMARY, ft.Colors.WHITE),
            "secondary": (AppTheme.SECONDARY, ft.Colors.BLACK),
            "success": (AppTheme.SUCCESS, ft.Colors.WHITE),
            "warning": (AppTheme.WARNING, ft.Colors.BLACK),
            "error": (AppTheme.ERROR, ft.Colors.WHITE),
        }
        bg_color, text_color = variant_colors.get(variant, variant_colors["primary"])

        # Get size dimensions
        sizes = {
            "sm": (20, 4),
            "md": (24, 6),
            "lg": (28, 8),
        }
        height, padding = sizes.get(size, sizes["md"])

        # Build content
        if count is not None:
            content = ft.Text(
                str(count),
                size=10,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            )
        else:
            content = ft.Text(
                text,
                size=10,
                weight=ft.FontWeight.W_500,
                color=text_color,
            )

        super().__init__(
            content=content,
            bgcolor=bg_color,
            height=height,
            padding=ft.padding.all(padding),
            border_radius=BorderRadius.FULL.value,
            alignment=ft.alignment.center,
            **kwargs
        )


class StatusBadge(ft.Container):
    """
    A status badge with icon and text for displaying entity status.

    Args:
        status: Status text
        variant: Status variant - 'active', 'inactive', 'pending', 'success', 'warning', 'error'
        size: Badge size - 'sm', 'md', 'lg'
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        status: str,
        variant: str = "active",
        size: str = "md",
        **kwargs
    ):
        # Get variant colors and icons
        from ui.components.icons import Icons

        variant_config = {
            "active": (AppTheme.SUCCESS, Icons.ACTIVE),
            "inactive": (AppTheme.DISABLED, Icons.INACTIVE),
            "pending": (AppTheme.WARNING, Icons.PENDING),
            "success": (AppTheme.SUCCESS, Icons.SUCCESS),
            "warning": (AppTheme.WARNING, Icons.WARNING),
            "error": (AppTheme.ERROR, Icons.ERROR),
        }
        color, icon = variant_config.get(variant, variant_config["active"])

        # Get size
        sizes = {
            "sm": 10,
            "md": 12,
            "lg": 14,
        }
        font_size = sizes.get(size, sizes["md"])

        # Build content
        content = ft.Row(
            [
                ft.Icon(
                    icon,
                    size=font_size + 4,
                    color=color,
                ),
                ft.Container(width=Spacing.XS.value),
                ft.Text(
                    status.capitalize(),
                    size=font_size,
                    weight=ft.FontWeight.W_600,
                    color=color,
                ),
            ],
            spacing=0,
        )

        # Build background color (light variant)
        light_colors = {
            "active": AppTheme.SUCCESS_LIGHT,
            "inactive": ft.Colors.GREY_200,
            "pending": AppTheme.WARNING_LIGHT,
            "success": AppTheme.SUCCESS_LIGHT,
            "warning": AppTheme.WARNING_LIGHT,
            "error": AppTheme.ERROR_LIGHT,
        }
        bg_color = light_colors.get(variant, ft.Colors.GREY_100)

        super().__init__(
            content=content,
            bgcolor=bg_color,
            padding=ft.padding.symmetric(
                horizontal=Spacing.SM.value,
                vertical=Spacing.XS.value
            ),
            border_radius=BorderRadius.SM.value,
            **kwargs
        )


class FilterChipGroup(ft.Row):
    """
    A group of filter chips with single selection.

    Args:
        options: List of (value, label) tuples
        selected: Initially selected value
        on_change: Callback when selection changes (value passed)
        **kwargs: Additional ft.Row properties
    """

    def __init__(
        self,
        options: list,
        selected: str = None,
        on_change=None,
        **kwargs
    ):
        self._chips = {}
        self._on_change = on_change
        self._selected = selected

        # Create chips
        chips = []
        for value, label in options:
            chip = AppChip(
                label=label,
                selected=(value == selected),
                on_click=lambda e, v=value: self._handle_click(v),
            )
            self._chips[value] = chip
            chips.append(chip)

        super().__init__(
            chips,
            spacing=Spacing.SM.value,
            **kwargs
        )

    def _handle_click(self, value: str):
        """Handle chip click."""
        # Update selected state
        self._selected = value

        # Update visuals
        for chip_value, chip in self._chips.items():
            chip.selected = (chip_value == value)

        # Call callback
        if self._on_change:
            self._on_change(value)

    @property
    def selected(self) -> str:
        """Get the selected value."""
        return self._selected
