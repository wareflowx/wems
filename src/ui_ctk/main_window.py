"""Main application window with navigation bar."""

from typing import Optional

import customtkinter as ctk

from ui_ctk.constants import (
    APP_TITLE,
    NAV_ALERTS,
    NAV_EMPLOYEES,
    NAV_IMPORT,
    NAV_BACKUPS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)
from ui_ctk.views.base_view import BaseView


class MainWindow(ctk.CTkFrame):
    """
    Main application window with navigation bar.

    Features:
    - Navigation bar with 3 main sections
    - Dynamic view container
    - View switching mechanism
    - Clean layout management
    """

    def __init__(self, master: ctk.CTk):
        """
        Initialize main window.

        Args:
            master: Root CTk application
        """
        super().__init__(master, fg_color="transparent")

        # Store reference to master for navigation
        self.master_window = master

        # Track current view
        self.current_view: Optional[BaseView] = None

        # Create UI components
        self.create_navigation_bar()
        self.create_view_container()

        # Show default view (employee list)
        self.show_employee_list()

    def create_navigation_bar(self):
        """Create navigation bar with buttons."""
        # Navigation container
        self.nav_bar = ctk.CTkFrame(self, height=60)
        self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)
        self.nav_bar.pack_propagate(False)

        # Title label
        title_label = ctk.CTkLabel(self.nav_bar, text=APP_TITLE, font=("Arial", 16, "bold"))
        title_label.pack(side="left", padx=20)

        # Button container (right side)
        button_container = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        button_container.pack(side="right")

        # Employee list button
        self.btn_employees = ctk.CTkButton(
            button_container, text=NAV_EMPLOYEES, width=120, command=self.show_employee_list
        )
        self.btn_employees.pack(side="left", padx=5)

        # Alerts button
        self.btn_alerts = ctk.CTkButton(button_container, text=NAV_ALERTS, width=120, command=self.show_alerts)
        self.btn_alerts.pack(side="left", padx=5)

        # Import button
        self.btn_import = ctk.CTkButton(button_container, text=NAV_IMPORT, width=140, command=self.show_import)
        self.btn_import.pack(side="left", padx=5)

        # Backups button
        self.btn_backups = ctk.CTkButton(
            button_container,
            text=NAV_BACKUPS,
            width=140,
            command=self.show_backups
        )
        self.btn_backups.pack(side="left", padx=5)

    def create_view_container(self):
        """Create container for dynamic views."""
        self.view_container = ctk.CTkFrame(self)
        self.view_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def clear_view(self):
        """Remove current view from container."""
        if self.current_view:
            # Call cleanup method if exists
            if hasattr(self.current_view, "cleanup"):
                try:
                    self.current_view.cleanup()
                except Exception as e:
                    print(f"[WARN] View cleanup error: {e}")

            # Destroy view
            self.current_view.destroy()
            self.current_view = None

    def switch_view(self, view_class: type, *args, **kwargs):
        """
        Switch to a new view.

        Args:
            view_class: View class to instantiate
            *args: Positional arguments for view constructor
            **kwargs: Keyword arguments for view constructor
        """
        # Remove current view
        self.clear_view()

        # Create new view
        self.current_view = view_class(self.view_container, *args, **kwargs)
        self.current_view.pack(fill="both", expand=True)

        # Update button states
        self.update_navigation_state()

    def update_navigation_state(self):
        """Update navigation button states to show active section."""
        # Reset all buttons to default state
        # Note: In future versions, we could highlight active button
        # For now, all buttons remain neutral
        pass

    # ===== Navigation Methods =====

    def show_employee_list(self):
        """Display employee list view."""
        try:
            from ui_ctk.views.employee_list import EmployeeListView

            self.switch_view(EmployeeListView, title="Liste des Employés")
            print("[NAV] Showing employee list view")
        except ImportError as e:
            print(f"[WARN] EmployeeListView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Liste des Employés")
            print("[NAV] Showing placeholder for employee list")
        except Exception as e:
            print(f"[ERROR] Failed to load employee list: {e}")
            self.show_error(f"Failed to load employee list: {e}")

    def show_alerts(self):
        """Display alerts view."""
        try:
            from ui_ctk.views.alerts_view import AlertsView

            self.switch_view(AlertsView, title="Alertes")
            print("[NAV] Showing alerts view")
        except ImportError as e:
            print(f"[WARN] AlertsView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Alertes")
            print("[NAV] Showing placeholder for alerts")
        except Exception as e:
            print(f"[ERROR] Failed to load alerts view: {e}")
            self.show_error(f"Failed to load alerts: {e}")

    def show_import(self):
        """Display import view."""
        try:
            from ui_ctk.views.import_view import ImportView

            self.switch_view(ImportView, title="Import Excel")
            print("[NAV] Showing import view")
        except ImportError as e:
            print(f"[WARN] ImportView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Import Excel")
            print("[NAV] Showing placeholder for import")
        except Exception as e:
            print(f"[ERROR] Failed to load import view: {e}")
            self.show_error(f"Failed to load import: {e}")

    def show_backups(self):
        """Display backup and export management view."""
        try:
            from ui_ctk.views.backup_view import BackupView
            self.switch_view(BackupView)
            print("[NAV] Showing backup view")
        except ImportError as e:
            print(f"[WARN] BackupView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView
            self.switch_view(PlaceholderView, title="Sauvegardes")
            print("[NAV] Showing placeholder for backups")
        except Exception as e:
            print(f"[ERROR] Failed to load backup view: {e}")
            self.show_error(f"Failed to load backup view: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Error", message)
        except:
            print(f"[ERROR] {message}")
