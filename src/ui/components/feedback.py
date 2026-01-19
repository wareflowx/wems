"""Feedback components for user communication.

Provides themed dialogs, snackbars, and confirmation prompts.
"""

import flet as ft
from typing import Callable, Optional
from ui.constants import Spacing, BorderRadius, IconSize
from ui.theme import AppTheme


class AppSnackBar(ft.SnackBar):
    """
    A themed snackbar for displaying temporary messages.

    Args:
        message: Message text to display
        variant: Style variant - 'info', 'success', 'warning', 'error'
        duration: Display duration in milliseconds (default 3000)
        action: Optional action button text
        action_handler: Optional action button handler
        **kwargs: Additional ft.SnackBar properties
    """

    def __init__(
        self,
        message: str,
        variant: str = "info",
        duration: int = 3000,
        action: str = None,
        action_handler: Callable = None,
        **kwargs
    ):
        from ui.components.icons import Icons, AppIcon

        # Get variant config
        variant_config = {
            "info": (AppTheme.INFO, Icons.INFO),
            "success": (AppTheme.SUCCESS, Icons.SUCCESS),
            "warning": (AppTheme.WARNING, Icons.WARNING),
            "error": (AppTheme.ERROR, Icons.ERROR),
        }
        color, icon = variant_config.get(variant, variant_config["info"])

        # Build content with icon
        content = ft.Row(
            [
                AppIcon(icon, size=IconSize.SM.value, color=ft.Colors.WHITE),
                ft.Container(width=Spacing.SM.value),
                ft.Text(
                    message,
                    color=ft.Colors.WHITE,
                    size=14,
                    expand=True,
                ),
            ],
            spacing=0,
        )

        # Build action if provided
        action_btn = None
        if action and action_handler:
            action_btn = ft.TextButton(
                action,
                style=ft.ButtonStyle(color=ft.Colors.WHITE),
                on_click=action_handler,
            )

        super().__init__(
            content=content,
            bgcolor=color,
            duration=duration,
            action=action_btn,
            **kwargs
        )


class AppDialog(ft.AlertDialog):
    """
    A themed dialog for displaying messages and forms.

    Args:
        title: Dialog title
        content: Dialog content (any Flet control)
        actions: List of action buttons
        icon: Optional icon to show in header
        **kwargs: Additional ft.AlertDialog properties
    """

    def __init__(
        self,
        title: str,
        content,
        actions: list = None,
        icon: str = None,
        **kwargs
    ):
        from ui.components.icons import AppIcon, IconSize

        # Build title with optional icon
        if icon:
            title_content = ft.Row(
                [
                    AppIcon(icon, size=IconSize.MD.value, color=AppTheme.PRIMARY),
                    ft.Container(width=Spacing.SM.value),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                spacing=0,
            )
        else:
            title_content = ft.Text(
                title,
                size=18,
                weight=ft.FontWeight.W_600,
            )

        super().__init__(
            title=title_content,
            content=content,
            actions=actions or [],
            **kwargs
        )


class ConfirmDialog(ft.AlertDialog):
    """
    A confirmation dialog for yes/no prompts.

    Args:
        title: Dialog title
        message: Confirmation message
        on_confirm: Callback when confirmed
        on_cancel: Callback when cancelled
        confirm_text: Confirm button text (default "Confirm")
        cancel_text: Cancel button text (default "Cancel")
        variant: Style variant for confirm button
        **kwargs: Additional ft.AlertDialog properties
    """

    def __init__(
        self,
        title: str,
        message: str,
        on_confirm: Callable = None,
        on_cancel: Callable = None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        variant: str = "primary",
        **kwargs
    ):
        from ui.components.icons import Icons
        from ui.components.buttons import AppButton

        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

        # Build content
        content = ft.Container(
            content=ft.Text(
                message,
                size=14,
            ),
            width=400,
            padding=ft.padding.symmetric(
                horizontal=Spacing.SM.value,
                vertical=Spacing.SM.value,
            ),
        )

        # Build actions
        actions = [
            ft.TextButton(
                cancel_text,
                on_click=self._handle_cancel,
            ),
            AppButton(
                confirm_text,
                variant=variant,
                on_click=self._handle_confirm,
            ),
        ]

        super().__init__(
            title=ft.Text(
                title,
                size=18,
                weight=ft.FontWeight.W_600,
            ),
            content=content,
            actions=actions,
            **kwargs
        )

    def _handle_confirm(self, e):
        """Handle confirm action."""
        if self._on_confirm:
            self._on_confirm(e)

    def _handle_cancel(self, e):
        """Handle cancel action."""
        if self._on_cancel:
            self._on_cancel(e)


class ErrorDialog(ft.AlertDialog):
    """
    An error dialog for displaying error messages.

    Args:
        title: Dialog title (default "Error")
        message: Error message
        on_close: Callback when dialog is closed
        **kwargs: Additional ft.AlertDialog properties
    """

    def __init__(
        self,
        title: str = "Error",
        message: str = "",
        on_close: Callable = None,
        **kwargs
    ):
        from ui.components.icons import Icons, AppIcon, IconSize

        self._on_close = on_close

        # Build content with error icon
        content = ft.Column(
            [
                ft.Row(
                    [
                        AppIcon(
                            Icons.ERROR,
                            size=IconSize.LG.value,
                            color=AppTheme.ERROR
                        ),
                        ft.Container(width=Spacing.MD.value),
                        ft.Text(
                            message,
                            size=14,
                        ),
                    ],
                    spacing=0,
                ),
            ],
        )

        # Build actions
        actions = [
            ft.TextButton(
                "Close",
                on_click=self._handle_close,
            ),
        ]

        super().__init__(
            title=ft.Text(
                title,
                size=18,
                weight=ft.FontWeight.W_600,
                color=AppTheme.ERROR,
            ),
            content=content,
            actions=actions,
            **kwargs
        )

    def _handle_close(self, e):
        """Handle close action."""
        if self._on_close:
            self._on_close(e)


class LoadingDialog(ft.AlertDialog):
    """
    A loading dialog with spinner for async operations.

    Args:
        message: Loading message
        **kwargs: Additional ft.AlertDialog properties
    """

    def __init__(self, message: str = "Loading...", **kwargs):
        content = ft.Column(
            [
                ft.ProgressRing(stroke_width=3),
                ft.Container(height=Spacing.MD.value),
                ft.Text(
                    message,
                    size=14,
                    color=AppTheme.ON_SURFACE_VARIANT,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        super().__init__(
            content=content,
            **kwargs
        )


class FormDialog(ft.AlertDialog):
    """
    A dialog container for forms with submit/cancel actions.

    Args:
        title: Dialog title
        form_content: Form content (any Flet control)
        on_submit: Submit callback
        on_cancel: Cancel callback
        submit_text: Submit button text
        cancel_text: Cancel button text
        submit_variant: Submit button style variant
        **kwargs: Additional ft.AlertDialog properties
    """

    def __init__(
        self,
        title: str,
        form_content,
        on_submit: Callable = None,
        on_cancel: Callable = None,
        submit_text: str = "Submit",
        cancel_text: str = "Cancel",
        submit_variant: str = "primary",
        **kwargs
    ):
        from ui.components.buttons import AppButton

        self._on_submit = on_submit
        self._on_cancel = on_cancel

        # Wrap content in container for consistent sizing
        wrapped_content = ft.Container(
            content=form_content,
            width=500,
            padding=ft.padding.symmetric(
                horizontal=Spacing.SM.value,
                vertical=Spacing.SM.value,
            ),
        )

        # Build actions
        actions = [
            ft.TextButton(
                cancel_text,
                on_click=self._handle_cancel,
            ),
            AppButton(
                submit_text,
                variant=submit_variant,
                on_click=self._handle_submit,
            ),
        ]

        super().__init__(
            title=ft.Text(
                title,
                size=18,
                weight=ft.FontWeight.W_600,
            ),
            content=wrapped_content,
            actions=actions,
            **kwargs
        )

    def _handle_submit(self, e):
        """Handle submit action."""
        if self._on_submit:
            self._on_submit(e)

    def _handle_cancel(self, e):
        """Handle cancel action."""
        if self._on_cancel:
            self._on_cancel(e)


def show_snackbar(
    page: ft.Page,
    message: str,
    variant: str = "info",
    duration: int = 3000,
    action: str = None,
    action_handler: Callable = None,
):
    """
    Show a snackbar message on the given page.

    Args:
        page: The Flet page instance
        message: Message to display
        variant: Style variant - 'info', 'success', 'warning', 'error'
        duration: Display duration in milliseconds
        action: Optional action button text
        action_handler: Optional action button handler
    """
    snackbar = AppSnackBar(
        message=message,
        variant=variant,
        duration=duration,
        action=action,
        action_handler=action_handler,
    )
    page.show_snack_bar(snackbar)


def show_confirm_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm: Callable = None,
    on_cancel: Callable = None,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    variant: str = "primary",
):
    """
    Show a confirmation dialog on the given page.

    Args:
        page: The Flet page instance
        title: Dialog title
        message: Confirmation message
        on_confirm: Callback when confirmed
        on_cancel: Callback when cancelled
        confirm_text: Confirm button text
        cancel_text: Cancel button text
        variant: Confirm button style variant
    """
    dialog = ConfirmDialog(
        title=title,
        message=message,
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        variant=variant,
    )
    page.show_dialog(dialog)


def show_error_dialog(
    page: ft.Page,
    message: str,
    title: str = "Error",
    on_close: Callable = None,
):
    """
    Show an error dialog on the given page.

    Args:
        page: The Flet page instance
        message: Error message
        title: Dialog title
        on_close: Callback when closed
    """
    dialog = ErrorDialog(
        title=title,
        message=message,
        on_close=on_close,
    )
    page.show_dialog(dialog)


def show_loading_dialog(
    page: ft.Page,
    message: str = "Loading...",
) -> ft.AlertDialog:
    """
    Show a loading dialog on the given page.

    Args:
        page: The Flet page instance
        message: Loading message

    Returns:
        The loading dialog instance (for closing later)
    """
    dialog = LoadingDialog(message=message)
    page.show_dialog(dialog)
    return dialog
