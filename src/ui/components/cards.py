"""Card components with consistent styling.

Provides themed card components for displaying content
with elevation and rounded corners.
"""

import flet as ft
from ui.constants import Spacing, BorderRadius
from ui.theme import AppTheme


class AppCard(ft.Container):
    """
    A themed card container with consistent styling.

    Args:
        content: Card content (any Flet control)
        title: Optional title text
        subtitle: Optional subtitle text
        icon: Optional icon for header
        padding: Internal padding (uses theme default if None)
        margin: External margin
        elevation: Shadow elevation (0-8)
        on_click: Optional click handler (makes card clickable)
        bgcolor: Background color (uses theme surface if None)
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        content,
        title: str = None,
        subtitle: str = None,
        icon: str = None,
        padding: int = None,
        margin: int = None,
        elevation: int = 2,
        on_click=None,
        bgcolor: str = None,
        **kwargs
    ):
        # Build card content
        card_content = []

        # Add header if title or icon provided
        if title or icon:
            header_elements = []
            if icon:
                from ui.components.icons import AppIcon, IconSize
                header_elements.append(
                    AppIcon(icon, size=IconSize.SM.value)
                )
                header_elements.append(ft.Container(width=Spacing.SM.value))

            if title:
                header_elements.append(
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=AppTheme.ON_SURFACE,
                    )
                )

            card_content.append(
                ft.Row(header_elements, spacing=0)
            )

            if subtitle:
                card_content.append(
                    ft.Text(
                        subtitle,
                        size=12,
                        color=AppTheme.ON_SURFACE_VARIANT,
                    )
                )

            card_content.append(ft.Divider(height=Spacing.SM.value))

        # Add main content
        card_content.append(content)

        # Build final content column
        final_content = ft.Column(
            card_content,
            spacing=Spacing.SM.value,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        # Card styling
        super().__init__(
            content=final_content,
            bgcolor=bgcolor or AppTheme.SURFACE,
            padding=padding or Spacing.MD.value,
            margin=margin,
            border_radius=BorderRadius.LG.value,
            on_click=on_click,
            ink=True if on_click else False,
            shadow=ft.BoxShadow(
                blur_radius=elevation * 2,
                spread_radius=elevation // 2,
                color=ft.Colors.with_opacity(
                    0.1 if elevation == 0 else 0.15,
                    ft.Colors.BLACK
                ),
                offset=ft.Offset(0, elevation),
            ) if elevation > 0 else None,
            **kwargs
        )


class StatCard(ft.Container):
    """
    A card for displaying statistics with icon and value.

    Args:
        label: Statistic label (e.g., "Total Employees")
        value: Statistic value (number or string)
        icon: Icon name (from Icons class)
        color: Accent color for icon and value
        trend: Optional trend indicator ('up', 'down', None)
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        label: str,
        value,
        icon: str,
        color: str,
        trend: str = None,
        **kwargs
    ):
        from ui.components.icons import AppIcon, IconSize

        # Build trend indicator
        trend_icon = None
        if trend:
            if trend == "up":
                trend_icon = AppIcon(
                    ft.icons.TRENDING_UP,
                    size=IconSize.XS.value,
                    color=AppTheme.SUCCESS
                )
            elif trend == "down":
                trend_icon = AppIcon(
                    ft.icons.TRENDING_DOWN,
                    size=IconSize.XS.value,
                    color=AppTheme.ERROR
                )

        # Build content
        content = ft.Column(
            [
                # Icon and value row
                ft.Row(
                    [
                        AppIcon(icon, size=IconSize.LG.value, color=color),
                        ft.Container(expand=True),
                        ft.Text(
                            str(value),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=color,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Label
                ft.Text(
                    label,
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=AppTheme.ON_SURFACE_VARIANT,
                ),
                # Trend if provided
                trend_icon if trend_icon else ft.Container(),
            ],
            spacing=Spacing.XS.value,
        )

        super().__init__(
            content=content,
            bgcolor=AppTheme.SURFACE,
            padding=Spacing.MD.value,
            border_radius=BorderRadius.LG.value,
            shadow=ft.BoxShadow(
                blur_radius=4,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            **kwargs
        )


class InfoCard(ft.Container):
    """
    A card for displaying informational messages.

    Args:
        message: Message text to display
        variant: Style variant - 'info', 'success', 'warning', 'error'
        icon: Optional icon override (auto-selected if None)
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        message: str,
        variant: str = "info",
        icon: str = None,
        **kwargs
    ):
        from ui.components.icons import AppIcon, IconSize, Icons

        # Auto-select icon if not provided
        if icon is None:
            icon_map = {
                "info": Icons.INFO,
                "success": Icons.SUCCESS,
                "warning": Icons.WARNING,
                "error": Icons.ERROR,
            }
            icon = icon_map.get(variant, Icons.INFO)

        # Get variant colors
        variant_colors = {
            "info": (AppTheme.INFO, AppTheme.INFO_LIGHT),
            "success": (AppTheme.SUCCESS, AppTheme.SUCCESS_LIGHT),
            "warning": (AppTheme.WARNING, AppTheme.WARNING_LIGHT),
            "error": (AppTheme.ERROR, AppTheme.ERROR_LIGHT),
        }
        icon_color, bg_color = variant_colors.get(
            variant,
            variant_colors["info"]
        )

        # Build content
        content = ft.Row(
            [
                AppIcon(icon, size=IconSize.MD.value, color=icon_color),
                ft.Container(width=Spacing.SM.value),
                ft.Text(
                    message,
                    size=14,
                    color=icon_color,
                    weight=ft.FontWeight.W_500,
                    expand=True,
                ),
            ],
            spacing=0,
        )

        super().__init__(
            content=content,
            bgcolor=bg_color,
            padding=ft.padding.symmetric(
                horizontal=Spacing.MD.value,
                vertical=Spacing.SM.value
            ),
            border_radius=BorderRadius.MD.value,
            **kwargs
        )
