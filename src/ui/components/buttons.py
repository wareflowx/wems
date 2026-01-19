"""Button components with consistent styling.

Provides theme-aware button components for different use cases.
"""

import flet as ft
from ui.constants import Spacing, BorderRadius, IconSize
from ui.theme import AppTheme
from ui.components.icons import Icons, AppIcon


class AppButton(ft.ElevatedButton):
    """
    A themed elevated button with consistent styling.

    Args:
        text: Button text label
        variant: Style variant - 'primary', 'secondary', 'success', 'warning', 'error', 'outline'
        icon: Optional icon name (from Icons class)
        on_click: Click handler
        disabled: Whether button is disabled
        expand: Whether button should expand to fill available space
        width: Fixed width (None for auto)
        **kwargs: Additional ft.Button properties
    """

    def __init__(
        self,
        text: str,
        variant: str = "primary",
        icon: str = None,
        on_click=None,
        disabled: bool = False,
        expand: int = None,
        width: int = None,
        **kwargs
    ):
        # Build button content
        content = None
        if icon:
            content = ft.Row(
                [
                    AppIcon(icon, size=IconSize.SM.value, color=ft.Colors.WHITE),
                    ft.Container(width=Spacing.XS.value),
                    ft.Text(text),
                ],
                spacing=0,
            )

        # Get style based on variant
        style = AppTheme.get_button_style(variant)
        if variant == "outline":
            # For outline buttons, add border
            style.side = ft.BorderSide(1, ft.Colors.BLUE)

        super().__init__(
            text=text if not icon else None,
            content=content,
            style=style,
            on_click=on_click,
            disabled=disabled,
            expand=expand,
            width=width,
            **kwargs
        )


class AppIconButton(ft.IconButton):
    """
    A themed icon button with consistent styling.

    Args:
        icon: Icon name (from Icons class)
        tooltip: Optional tooltip text
        on_click: Click handler
        icon_color: Icon color (uses theme primary if None)
        icon_size: Icon size
        **kwargs: Additional ft.IconButton properties
    """

    def __init__(
        self,
        icon: str,
        tooltip: str = None,
        on_click=None,
        icon_color: str = None,
        icon_size: int = IconSize.MD.value,
        **kwargs
    ):
        super().__init__(
            icon=icon,
            tooltip=tooltip,
            on_click=on_click,
            icon_color=icon_color or AppTheme.PRIMARY,
            icon_size=icon_size,
            **kwargs
        )


class ActionButton(ft.Container):
    """
    A button with icon and text for action menus.

    Commonly used in action bars and toolbars.

    Args:
        text: Button text label
        icon: Icon name (from Icons class)
        on_click: Click handler
        variant: Style variant
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        text: str,
        icon: str,
        on_click=None,
        variant: str = "primary",
        **kwargs
    ):
        # Get colors based on variant
        colors = {
            "primary": (AppTheme.PRIMARY, ft.Colors.WHITE),
            "secondary": (AppTheme.SECONDARY, ft.Colors.BLACK),
            "success": (AppTheme.SUCCESS, ft.Colors.WHITE),
            "warning": (AppTheme.WARNING, ft.Colors.BLACK),
            "error": (AppTheme.ERROR, ft.Colors.WHITE),
        }
        bgcolor, text_color = colors.get(variant, colors["primary"])

        super().__init__(
            content=ft.Row(
                [
                    AppIcon(icon, size=IconSize.SM.value, color=text_color),
                    ft.Container(width=Spacing.XS.value),
                    ft.Text(
                        text,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=text_color
                    ),
                ],
                spacing=0,
            ),
            bgcolor=bgcolor,
            padding=ft.padding.symmetric(
                horizontal=Spacing.MD.value,
                vertical=Spacing.SM.value
            ),
            border_radius=BorderRadius.MD.value,
            on_click=on_click,
            **kwargs
        )


class FloatingActionButton(ft.Container):
    """
    A floating action button (FAB) for primary actions.

    Args:
        icon: Icon name (from Icons class)
        tooltip: Tooltip text
        on_click: Click handler
        bgcolor: Background color (uses theme primary if None)
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        icon: str,
        tooltip: str,
        on_click=None,
        bgcolor: str = None,
        **kwargs
    ):
        super().__init__(
            content=AppIcon(
                icon,
                size=IconSize.MD.value,
                color=ft.Colors.WHITE
            ),
            width=56,
            height=56,
            bgcolor=bgcolor or AppTheme.PRIMARY,
            border_radius=BorderRadius.FULL.value,
            alignment=ft.alignment.center,
            tooltip=tooltip,
            on_click=on_click,
            shadow=ft.BoxShadow(
                blur_radius=8,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            **kwargs
        )
