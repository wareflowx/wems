"""Base class for all forms."""

from typing import Optional, Tuple

import customtkinter as ctk

from ui_ctk.constants import APP_TITLE


class BaseFormDialog(ctk.CTkToplevel):
    """Base class for form dialogs."""

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

    def create_form(self):
        """Create form content. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement create_form()")

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
            self.destroy()
        except Exception as e:
            self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")

    def on_cancel(self):
        """Handle cancel button click."""
        self.result = False
        self.destroy()

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
