"""Input field components with consistent styling.

Provides themed input components for text, dropdowns, and other form inputs.
"""

import flet as ft
from typing import List, Tuple, Optional, Callable
from ui.constants import Spacing, BorderRadius
from ui.theme import AppTheme


class AppTextField(ft.TextField):
    """
    A themed text input field with consistent styling.

    Args:
        label: Field label
        hint_text: Placeholder text
        value: Initial value
        on_change: Change handler
        required: Whether field is required (shows asterisk)
        password: Whether to hide text (password field)
        multiline: Whether to allow multiple lines
        max_lines: Maximum number of lines (for multiline)
        prefix_icon: Optional prefix icon
        suffix_icon: Optional suffix icon
        readonly: Whether field is read-only
        **kwargs: Additional ft.TextField properties
    """

    def __init__(
        self,
        label: str = None,
        hint_text: str = None,
        value: str = None,
        on_change: Callable = None,
        required: bool = False,
        password: bool = False,
        multiline: bool = False,
        max_lines: int = None,
        prefix_icon: str = None,
        suffix_icon: str = None,
        readonly: bool = False,
        **kwargs
    ):
        # Format label with required marker
        formatted_label = label
        if label and required:
            formatted_label = f"{label} *"

        super().__init__(
            label=formatted_label,
            hint_text=hint_text,
            value=value,
            on_change=on_change,
            password=password,
            multiline=multiline,
            max_lines=max_lines,
            prefix_icon=prefix_icon,
            suffix_icon=suffix_icon,
            read_only=readonly,
            border_radius=BorderRadius.MD.value,
            filled=True,
            **kwargs
        )


class AppDropdown(ft.Dropdown):
    """
    A themed dropdown select field with consistent styling.

    Args:
        label: Field label
        options: List of (key, value) tuples or ft.dropdown.Option objects
        value: Initial selected value
        on_change: Change handler
        required: Whether field is required
        hint_text: Placeholder text
        **kwargs: Additional ft.Dropdown properties
    """

    def __init__(
        self,
        label: str = None,
        options: List = None,
        value: str = None,
        on_change: Callable = None,
        required: bool = False,
        hint_text: str = None,
        **kwargs
    ):
        # Format label with required marker
        formatted_label = label
        if label and required:
            formatted_label = f"{label} *"

        # Build dropdown options
        dropdown_options = []
        if options:
            for opt in options:
                if isinstance(opt, ft.dropdown.Option):
                    dropdown_options.append(opt)
                elif isinstance(opt, tuple) and len(opt) == 2:
                    dropdown_options.append(
                        ft.dropdown.Option(opt[0], opt[1])
                    )

        super().__init__(
            label=formatted_label,
            options=dropdown_options,
            value=value,
            on_change=on_change,
            hint_text=hint_text,
            border_radius=BorderRadius.MD.value,
            filled=True,
            **kwargs
        )


class SearchField(ft.Container):
    """
    A themed search input field with icon.

    Args:
        placeholder: Placeholder text
        on_change: Change handler
        on_submit: Submit handler (press Enter)
        width: Field width (None for responsive)
        autofocus: Whether to autofocus on mount
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        placeholder: str = "Search...",
        on_change: Callable = None,
        on_submit: Callable = None,
        width: int = None,
        autofocus: bool = False,
        **kwargs
    ):
        from ui.components.icons import Icons

        self._on_submit = on_submit

        search_input = ft.TextField(
            hint_text=placeholder,
            on_change=on_change,
            on_submit=self._handle_submit,
            prefix_icon=Icons.SEARCH,
            border_radius=BorderRadius.FULL.value,
            filled=True,
            autofocus=autofocus,
            expand=True,
        )

        super().__init__(
            content=search_input,
            width=width,
            **kwargs
        )

    def _handle_submit(self, e):
        """Handle submit event."""
        if self._on_submit:
            self._on_submit(e)


class DatePickerField(ft.Container):
    """
    A date picker input field.

    Args:
        label: Field label
        value: Initial date value (datetime.date)
        on_change: Change handler
        required: Whether field is required
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        label: str = None,
        value = None,
        on_change: Callable = None,
        required: bool = False,
        **kwargs
    ):
        from ui.components.icons import Icons, AppIcon, IconSize

        self._on_change = on_change
        self._value = value

        # Format label
        formatted_label = label
        if label and required:
            formatted_label = f"{label} *"

        # Date button
        date_text = value.strftime("%d/%m/%Y") if value else "Select date"

        self.date_button = ft.ElevatedButton(
            date_text,
            icon=Icons.CALENDAR,
            on_click=self._pick_date,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD.value),
            ),
            expand=True,
        )

        # Build field row
        content = ft.Column(
            [
                ft.Text(
                    formatted_label,
                    size=14,
                    weight=ft.FontWeight.W_500,
                ) if formatted_label else None,
                ft.Row(
                    [self.date_button],
                    expand=True,
                ),
            ],
            spacing=Spacing.XS.value,
        )

        super().__init__(content=content, **kwargs)

    def _pick_date(self, e):
        """Show date picker dialog."""
        # Note: Full date picker implementation requires
        # Flet's DatePicker which is in beta
        # For now, this is a placeholder
        pass

    @property
    def value(self):
        """Get the current date value."""
        return self._value

    def set_value(self, value):
        """Set the date value."""
        self._value = value
        if value:
            self.date_button.text = value.strftime("%d/%m/%Y")
        else:
            self.date_button.text = "Select date"


class FormSection(ft.Container):
    """
    A section container for grouping related form fields.

    Args:
        title: Section title
        fields: List of form field widgets
        collapsible: Whether section can be collapsed
        **kwargs: Additional ft.Container properties
    """

    def __init__(
        self,
        title: str,
        fields: List,
        collapsible: bool = False,
        **kwargs
    ):
        from ui.components.icons import AppIcon, IconSize, Icons

        self._fields_content = ft.Column(
            fields,
            spacing=Spacing.MD.value,
        )

        # Header with title
        header = ft.Row(
            [
                ft.Icon(
                    ft.icons.TAB,
                    size=IconSize.SM.value,
                    color=AppTheme.PRIMARY
                ),
                ft.Container(width=Spacing.SM.value),
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=AppTheme.PRIMARY,
                ),
            ],
            spacing=0,
        )

        content = ft.Column(
            [
                header,
                ft.Divider(height=1),
                self._fields_content,
            ],
            spacing=Spacing.SM.value,
        )

        super().__init__(
            content=content,
            padding=Spacing.MD.value,
            bgcolor=AppTheme.SURFACE_VARIANT,
            border_radius=BorderRadius.LG.value,
            **kwargs
        )
