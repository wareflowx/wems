"""Base class for all forms."""

from typing import Optional, Tuple

import customtkinter as ctk

from ui_ctk.constants import APP_TITLE
from utils.state_tracker import FormStateManager


class BaseFormDialog(ctk.CTkToplevel):
    """Base class for form dialogs with unsaved changes tracking."""

    def __init__(self, parent, title: str, width: int = 500, height: int = 600):
        """
        Initialize form dialog.

        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width
            height: Dialog height
        """
        super().__init__(parent)
        self.title(f"{APP_TITLE} - {title}")
        self.geometry(f"{width}x{height}")
        self.result = None  # Set to True if saved successfully

        # Initialize state manager for unsaved changes tracking
        self.state_manager = FormStateManager(self)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        # Create form content
        self.create_form()

        # Capture initial state after form creation
        self._bind_change_events()
        self.state_manager.capture_initial_state()

        # Bind window close protocol
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def create_form(self):
        """Create form content. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement create_form()")

    def _bind_change_events(self):
        """Bind change events to tracked variables.

        This method attaches trace callbacks to all tracked variables
        to detect when form fields are modified.
        """
        # Bind events to tracked variables
        for attr_name, var in self.state_manager._tracked_vars.items():
            try:
                # Use trace_add to watch for write operations
                var.trace_add('write', self._on_field_changed)
            except Exception as e:
                # Variable might not support tracing, skip it
                print(f"[WARN] Could not bind trace to {attr_name}: {e}")

    def _on_window_close(self):
        """Handle window close button (X) click.

        Checks for unsaved changes before closing.
        """
        # Check for unsaved changes
        if self.has_unsaved_changes():
            response = self._prompt_unsaved_changes()
            if response == 'cancel':
                return  # Don't close
            elif response == 'save':
                # Try to save
                is_valid, error = self.validate()
                if not is_valid:
                    self.show_error(error)
                    return
                try:
                    self.save()
                    self.result = True
                    self.state_manager.mark_as_saved()
                except Exception as e:
                    self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")
                    return
            # else: 'discard' - continue to close

        # Close the window
        self.destroy()

    def _on_field_changed(self, *args):
        """Callback when a form field changes.

        This is triggered automatically when any tracked variable is modified.
        Updates the unsaved changes status and shows/hides indicator.
        """
        # Update unsaved status
        if self.state_manager.update_has_unsaved():
            self._show_unsaved_indicator()
        else:
            self._hide_unsaved_indicator()

    def _show_unsaved_indicator(self):
        """Show unsaved changes indicator in the form.

        Override in subclasses to add visual indicator.
        Default implementation does nothing.
        """
        pass

    def _hide_unsaved_indicator(self):
        """Hide unsaved changes indicator from the form.

        Override in subclasses to remove visual indicator.
        Default implementation does nothing.
        """
        pass

    def has_unsaved_changes(self) -> bool:
        """Check if form has unsaved changes.

        Returns:
            True if form has unsaved changes, False otherwise
        """
        return self.state_manager.has_unsaved_changes

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate form data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        raise NotImplementedError("Subclasses must implement validate()")

    def save(self):
        """Save form data. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement save()")

    def on_save(self):
        """Handle save button click."""
        is_valid, error = self.validate()

        if not is_valid:
            self.show_error(error)
            return

        try:
            self.save()
            self.result = True

            # Mark form as saved
            self.state_manager.mark_as_saved()
            self._hide_unsaved_indicator()

            self.destroy()
        except Exception as e:
            self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")

    def on_cancel(self):
        """Handle cancel button click.

        Checks for unsaved changes before closing.
        """
        # Check for unsaved changes
        if self.has_unsaved_changes():
            response = self._prompt_unsaved_changes()
            if response == 'cancel':
                return  # Don't close
            elif response == 'save':
                # Try to save
                is_valid, error = self.validate()
                if not is_valid:
                    self.show_error(error)
                    return
                try:
                    self.save()
                    self.result = True
                    self.state_manager.mark_as_saved()
                except Exception as e:
                    self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")
                    return
            # else: 'discard' - continue to close

        self.result = False
        self.destroy()

    def _prompt_unsaved_changes(self) -> str:
        """Prompt user about unsaved changes.

        Returns:
            'save', 'discard', or 'cancel'
        """
        try:
            import tkinter.messagebox as messagebox
            import tkinter as tk

            # Create a custom dialog with Yes/No/Cancel
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes in this form.\n\n"
                "Do you want to save them before closing?",
                icon='warning'
            )

            if response is None:  # Cancel
                return 'cancel'
            elif response:  # Yes - save
                return 'save'
            else:  # No - discard
                return 'discard'
        except Exception:
            # Fallback if messagebox fails
            return 'discard'

    def show_error(self, message: str):
        """Show error message to user."""
        # Create error label if it doesn't exist
        if not hasattr(self, "error_label"):
            self.error_label = ctk.CTkLabel(self, text="", text_color="red", wraplength=400)
            self.error_label.pack(pady=10)

        self.error_label.configure(text=message)

    def clear_error(self):
        """Clear error message."""
        if hasattr(self, "error_label"):
            self.error_label.configure(text="")
