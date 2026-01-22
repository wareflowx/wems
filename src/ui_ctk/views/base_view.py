"""Base class for all views."""

import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    """Base class for all application views."""

    def __init__(self, master, title: str = ""):
        """
        Initialize base view.

        Args:
            master: Parent widget
            title: View title (optional)
        """
        super().__init__(master, fg_color="transparent")

        self.title = title
        self.master_window = self._find_main_window(master)  # Find MainWindow for navigation

        # Create header if title provided
        if title:
            self.create_header()

    def _find_main_window(self, widget):
        """
        Find the MainWindow instance by walking up the widget hierarchy.

        Args:
            widget: Starting widget

        Returns:
            MainWindow instance or None if not found
        """
        current = widget
        while current is not None:
            # Check if this is the MainWindow (has switch_view method)
            if hasattr(current, "switch_view") and hasattr(current, "show_employee_list"):
                return current
            # Move up to parent
            current = current.master
        return None

    def create_header(self):
        """Create view header with title."""
        header = ctk.CTkLabel(self, text=self.title, font=("Arial", 20, "bold"))
        header.pack(pady=10)

    def refresh(self):
        """
        Refresh view data.

        Override in subclasses to implement refresh logic.
        """
        pass

    def cleanup(self):
        """
        Cleanup resources when view is destroyed.

        Override in subclasses if needed.
        """
        pass

    def show_employee_list(self):
        """Navigate to employee list view."""
        if self.master_window and hasattr(self.master_window, "show_employee_list"):
            self.master_window.show_employee_list()

    def show_alerts(self):
        """Navigate to alerts view."""
        if self.master_window and hasattr(self.master_window, "show_alerts"):
            self.master_window.show_alerts()

    def show_import(self):
        """Navigate to import view."""
        if self.master_window and hasattr(self.master_window, "show_import"):
            self.master_window.show_import()
