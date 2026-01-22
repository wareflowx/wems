"""Employee list view with search and filtering."""

from typing import List

import customtkinter as ctk

from employee.models import Employee
from ui_ctk.constants import (
    BTN_ADD,
    BTN_REFRESH,
    BTN_VIEW,
    COLOR_INACTIVE,
    COLOR_SUCCESS,
    FILTER_ALL,
    PLACEHOLDER_SEARCH,
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    TABLE_ACTIONS,
    TABLE_EMAIL,
    TABLE_NAME,
    TABLE_PHONE,
    TABLE_ROLE,
    TABLE_STATUS,
)
from ui_ctk.views.base_view import BaseView


class EmployeeListView(BaseView):
    """
    Employee list view with search and filter capabilities.

    Features:
    - Display employees in scrollable table
    - Real-time search by name
    - Filter by status (active/inactive)
    - Click to view employee detail
    - Add new employee button
    """

    def __init__(self, master, title: str = "Liste des Employés"):
        super().__init__(master, title)

        # State
        self.employees: List[Employee] = []
        self.filtered_employees: List[Employee] = []
        self.table_rows: List[ctk.CTkFrame] = []

        # Search and filter variables
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        self.filter_var = ctk.StringVar(value=FILTER_ALL)

        # UI Components
        self.create_controls()
        self.create_table()

        # Load data
        self.refresh_employee_list()

    def create_controls(self):
        """Create search and filter controls."""
        # Control frame
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        control_frame.pack_propagate(False)

        # Search entry
        search_label = ctk.CTkLabel(control_frame, text="Rechercher:", font=("Arial", 12))
        search_label.pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(
            control_frame, placeholder_text=PLACEHOLDER_SEARCH, textvariable=self.search_var, width=300
        )
        self.search_entry.pack(side="left", padx=5)

        # Filter dropdown
        filter_label = ctk.CTkLabel(control_frame, text="Statut:", font=("Arial", 12))
        filter_label.pack(side="left", padx=(20, 5))

        self.filter_menu = ctk.CTkOptionMenu(
            control_frame,
            values=[FILTER_ALL, STATUS_ACTIVE, STATUS_INACTIVE],
            variable=self.filter_var,
            command=self.on_filter_changed,
            width=120,
        )
        self.filter_menu.pack(side="left", padx=5)

        # Buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        # Add employee button
        self.add_btn = ctk.CTkButton(button_frame, text=f"+ {BTN_ADD}", width=120, command=self.add_employee)
        self.add_btn.pack(side="left", padx=5)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(button_frame, text=BTN_REFRESH, width=120, command=self.refresh_employee_list)
        self.refresh_btn.pack(side="left", padx=5)

    def create_table(self):
        """Create employee table."""
        # Scrollable frame for table
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))

        # Create header
        self.create_table_header()

    def create_table_header(self):
        """Create table header row."""
        header = ctk.CTkFrame(self.table_frame, height=40, fg_color=("gray80", "gray25"))
        header.pack(fill="x", pady=(0, 5))
        header.pack_propagate(False)

        # Header columns
        columns = [
            (TABLE_NAME, 250),
            (TABLE_EMAIL, 200),
            (TABLE_PHONE, 120),
            (TABLE_ROLE, 150),
            (TABLE_STATUS, 100),
            (TABLE_ACTIONS, 100),
        ]

        for col_name, col_width in columns:
            label = ctk.CTkLabel(header, text=col_name, font=("Arial", 12, "bold"), anchor="w")
            label.pack(side="left", padx=10, pady=5)

    def refresh_employee_list(self):
        """Load employees from database."""
        # Fetch all employees
        self.employees = list(Employee.select().order_by(Employee.last_name, Employee.first_name))

        # Apply filters
        self.apply_filters()

        # Refresh table
        self.refresh_table()

        print(f"[INFO] Loaded {len(self.filtered_employees)} employees")

    def apply_filters(self):
        """Apply search and filter to employee list."""
        # Start with all employees
        filtered = self.employees

        # Apply status filter
        filter_value = self.filter_var.get()
        if filter_value == STATUS_ACTIVE:
            filtered = [e for e in filtered if e.is_active]
        elif filter_value == STATUS_INACTIVE:
            filtered = [e for e in filtered if not e.is_active]

        # Apply search filter
        search_term = self.search_var.get().lower().strip()
        if search_term:
            filtered = [
                e
                for e in filtered
                if search_term in e.first_name.lower()
                or search_term in e.last_name.lower()
                or (e.email and search_term in e.email.lower())
                or (e.phone and search_term in e.phone)
            ]

        self.filtered_employees = filtered

    def refresh_table(self):
        """Rebuild table rows."""
        # Clear existing rows
        for row in self.table_rows:
            row.destroy()
        self.table_rows.clear()

        # Create new rows
        for employee in self.filtered_employees:
            row = self.create_employee_row(employee)
            row.pack(fill="x", pady=2)
            self.table_rows.append(row)

        # Show count
        self.show_employee_count()

    def create_employee_row(self, employee: Employee) -> ctk.CTkFrame:
        """
        Create a single employee row.

        Args:
            employee: Employee object

        Returns:
            Frame containing employee row
        """
        row = ctk.CTkFrame(self.table_frame, height=50)
        row.pack_propagate(False)

        # Name
        name_label = ctk.CTkLabel(row, text=employee.full_name, font=("Arial", 13), anchor="w")
        name_label.pack(side="left", padx=10, pady=5)

        # Email
        email_text = employee.email if employee.email else "-"
        email_label = ctk.CTkLabel(row, text=email_text, font=("Arial", 11), anchor="w", width=200)
        email_label.pack(side="left", padx=10)

        # Phone
        phone_text = employee.phone if employee.phone else "-"
        phone_label = ctk.CTkLabel(row, text=phone_text, font=("Arial", 11), anchor="w", width=120)
        phone_label.pack(side="left", padx=10)

        # Role
        role_label = ctk.CTkLabel(row, text=employee.role, font=("Arial", 11), anchor="w", width=150)
        role_label.pack(side="left", padx=10)

        # Status
        status_text = STATUS_ACTIVE if employee.is_active else STATUS_INACTIVE
        status_color = COLOR_SUCCESS if employee.is_active else COLOR_INACTIVE
        status_label = ctk.CTkLabel(
            row, text=status_text, font=("Arial", 11, "bold"), text_color=status_color, width=100
        )
        status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        detail_btn = ctk.CTkButton(
            action_frame, text=BTN_VIEW, width=80, height=28, command=lambda: self.show_employee_detail(employee)
        )
        detail_btn.pack()

        return row

    def show_employee_detail(self, employee: Employee):
        """Navigate to employee detail view."""
        try:
            # Get main window
            main_window = self.master_window

            # Import detail view
            from ui_ctk.views.employee_detail import EmployeeDetailView

            # Switch to detail view
            main_window.switch_view(EmployeeDetailView, employee=employee)

            print(f"[NAV] Showing detail for {employee.full_name}")

        except Exception as e:
            print(f"[ERROR] Failed to show employee detail: {e}")
            self.show_error(f"Failed to load employee detail: {e}")

    def add_employee(self):
        """Open dialog to add new employee."""
        try:
            from ui_ctk.forms.employee_form import EmployeeFormDialog

            # Open form dialog
            dialog = EmployeeFormDialog(self, title="Employé")

            # Wait for dialog to close
            self.wait_window(dialog)

            # If employee was created, refresh list
            if dialog.result:
                print(f"[INFO] Employee created: {dialog.result.full_name}")
                self.refresh_employee_list()

        except Exception as e:
            print(f"[ERROR] Failed to open employee form: {e}")
            self.show_error(f"Failed to open employee form: {e}")

    def on_search_changed(self, *args):
        """Handle search text change."""
        self.apply_filters()
        self.refresh_table()

    def on_filter_changed(self, value):
        """Handle filter dropdown change."""
        self.apply_filters()
        self.refresh_table()

    def show_employee_count(self):
        """Display employee count."""
        # Update title with count
        count = len(self.filtered_employees)
        total = len(self.employees)

        if count == total:
            count_text = f"{count} employé(s)"
        else:
            count_text = f"{count} / {total} employé(s)"

        # Update header label if it exists
        if hasattr(self, "header_label"):
            self.header_label.configure(text=f"Liste des Employés - {count_text}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Erreur", message)
        except:
            print(f"[ERROR] {message}")

    def refresh(self):
        """Refresh the view (called by parent)."""
        self.refresh_employee_list()
