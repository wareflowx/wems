"""Employee form dialog for creating and editing employees."""

import re
from datetime import date, datetime
from typing import Optional

import customtkinter as ctk

from employee.constants import EmployeeStatus
from employee.models import Employee
from ui_ctk.constants import (
    BTN_CANCEL,
    BTN_SAVE,
    CONTRACT_TYPE_CHOICES,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    ERROR_SAVE_EMPLOYEE,
    ROLE_CHOICES,
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    VALIDATION_DATE_FUTURE,
    VALIDATION_DATE_INVALID,
    VALIDATION_DATE_REQUIRED,
    VALIDATION_DATE_TOO_OLD,
    VALIDATION_EMAIL_INVALID,
    VALIDATION_FIRST_NAME_REQUIRED,
    VALIDATION_LAST_NAME_REQUIRED,
    VALIDATION_PHONE_INVALID,
    VALIDATION_ROLE_REQUIRED,
    VALIDATION_WORKSPACE_REQUIRED,
    WORKSPACE_ZONES,
)
from ui_ctk.forms.base_form import BaseFormDialog


class EmployeeFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing employees.

    Features:
    - Create or edit mode
    - Field validation
    - Required field indicators
    - French date format
    """

    def __init__(self, parent, employee: Optional[Employee] = None, title: str = "Employé"):
        """
        Initialize form dialog.

        Args:
            parent: Parent window
            employee: Employee to edit (None for new employee)
            title: Dialog title
        """
        # Determine mode
        self.employee = employee
        self.is_edit_mode = employee is not None

        # Set title
        if self.is_edit_mode:
            full_title = f"Modifier - {employee.full_name}"
        else:
            full_title = f"Ajouter un {title}"

        # Form variables (must be set before calling parent init)
        self.first_name_var = ctk.StringVar()
        self.last_name_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value=STATUS_ACTIVE)
        self.workspace_var = ctk.StringVar()
        self.role_var = ctk.StringVar()
        self.contract_type_var = ctk.StringVar(value=CONTRACT_TYPE_CHOICES[0])
        self.entry_date_var = ctk.StringVar()

        # Initialize parent
        super().__init__(parent, title=full_title, width=600, height=700)

        # Load employee data if editing
        if self.is_edit_mode:
            self.load_employee_data()

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Modifier un Employé" if self.is_edit_mode else "Nouvel Employé"
        title_label = ctk.CTkLabel(form_frame, text=title, font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))

        # Required fields notice
        notice_label = ctk.CTkLabel(form_frame, text="* Champs obligatoires", font=("Arial", 10), text_color="gray")
        notice_label.pack(pady=(0, 10))

        # Form fields
        self.create_field_section(form_frame)

        # Buttons
        self.create_buttons(form_frame)

    def create_field_section(self, parent):
        """Create form field section."""
        # Field container
        field_container = ctk.CTkScrollableFrame(parent)
        field_container.pack(fill="both", expand=True)

        # Row 1: First Name, Last Name
        row1 = ctk.CTkFrame(field_container, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.create_required_field(row1, "Prénom:", self.first_name_var, "Jean", 0)
        self.create_required_field(row1, "Nom:", self.last_name_var, "Dupont", 1)

        # Row 2: Email, Phone
        row2 = ctk.CTkFrame(field_container, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.create_optional_field(row2, "Email:", self.email_var, "jean@example.com", 0)
        self.create_optional_field(row2, "Téléphone:", self.phone_var, "06 12 34 56 78", 1)

        # Row 3: Status, Workspace
        row3 = ctk.CTkFrame(field_container, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        self.create_status_dropdown(row3, "Statut:", self.status_var, 0)
        self.create_workspace_dropdown(row3, "Zone de travail:", self.workspace_var, 1)

        # Row 4: Role, Contract Type
        row4 = ctk.CTkFrame(field_container, fg_color="transparent")
        row4.pack(fill="x", pady=5)

        self.create_role_dropdown(row4, "Poste:", self.role_var, 0)
        self.create_contract_dropdown(row4, "Type de contrat:", self.contract_type_var, 1)

        # Row 5: Entry Date
        row5 = ctk.CTkFrame(field_container, fg_color="transparent")
        row5.pack(fill="x", pady=5)

        self.create_date_field(row5, "Date d'entrée:", self.entry_date_var, 0)

    def create_required_field(self, parent, label: str, variable: ctk.StringVar, placeholder: str, column: int):
        """Create a required form field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label with required indicator
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Entry
        entry = ctk.CTkEntry(container, placeholder_text=placeholder, textvariable=variable)
        entry.pack(fill="x", pady=(0, 5))

    def create_optional_field(self, parent, label: str, variable: ctk.StringVar, placeholder: str, column: int):
        """Create an optional form field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=label, font=("Arial", 11), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Entry
        entry = ctk.CTkEntry(container, placeholder_text=placeholder, textvariable=variable)
        entry.pack(fill="x", pady=(0, 5))

    def create_status_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create status dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(container, values=[STATUS_ACTIVE, STATUS_INACTIVE], variable=variable, width=200)
        dropdown.pack(fill="x", pady=(0, 5))

    def create_workspace_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create workspace dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(container, values=WORKSPACE_ZONES, variable=variable, width=200)
        dropdown.pack(fill="x", pady=(0, 5))

    def create_role_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create role dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(container, values=ROLE_CHOICES, variable=variable, width=200)
        dropdown.pack(fill="x", pady=(0, 5))

    def create_contract_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create contract type dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(container, values=CONTRACT_TYPE_CHOICES, variable=variable, width=200)
        dropdown.pack(fill="x", pady=(0, 5))

    def create_date_field(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create date entry field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(container, text=f"{label} *", font=("Arial", 11, "bold"), anchor="w")
        label_widget.pack(fill="x", pady=(5, 2))

        # Date entry
        date_entry = ctk.CTkEntry(container, placeholder_text=DATE_PLACEHOLDER, textvariable=variable)
        date_entry.pack(fill="x", pady=(0, 5))

        # Format hint
        hint_label = ctk.CTkLabel(container, text=f"Format: {DATE_FORMAT}", font=("Arial", 9), text_color="gray")
        hint_label.pack(anchor="w")

    def create_buttons(self, parent):
        """Create form buttons."""
        # Button container
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, text=BTN_CANCEL, width=120, command=self.cancel, fg_color="gray")
        cancel_btn.pack(side="right", padx=5)

        # Save button
        save_btn = ctk.CTkButton(button_frame, text=BTN_SAVE, width=120, command=self.save)
        save_btn.pack(side="right", padx=5)

    def load_employee_data(self):
        """Load existing employee data into form."""
        if not self.employee:
            return

        self.first_name_var.set(self.employee.first_name)
        self.last_name_var.set(self.employee.last_name)
        self.email_var.set(self.employee.email or "")
        self.phone_var.set(self.employee.phone or "")
        self.status_var.set(STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE)
        self.workspace_var.set(self.employee.workspace)
        self.role_var.set(self.employee.role)
        self.contract_type_var.set(self.employee.contract_type)

        # Format entry date
        if self.employee.entry_date:
            entry_date_str = self.employee.entry_date.strftime(DATE_FORMAT)
            self.entry_date_var.set(entry_date_str)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate form fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields
        first_name = self.first_name_var.get().strip()
        if not first_name:
            return False, VALIDATION_FIRST_NAME_REQUIRED

        last_name = self.last_name_var.get().strip()
        if not last_name:
            return False, VALIDATION_LAST_NAME_REQUIRED

        workspace = self.workspace_var.get().strip()
        if not workspace:
            return False, VALIDATION_WORKSPACE_REQUIRED

        role = self.role_var.get().strip()
        if not role:
            return False, VALIDATION_ROLE_REQUIRED

        # Email validation (if provided)
        email = self.email_var.get().strip()
        if email:
            if not self.validate_email(email):
                return False, VALIDATION_EMAIL_INVALID

        # Phone validation (if provided)
        phone = self.phone_var.get().strip()
        if phone:
            if not self.validate_phone(phone):
                return False, VALIDATION_PHONE_INVALID

        # Date validation
        entry_date_str = self.entry_date_var.get().strip()
        if not entry_date_str:
            return False, VALIDATION_DATE_REQUIRED

        try:
            entry_date = datetime.strptime(entry_date_str, DATE_FORMAT).date()
        except ValueError:
            return False, f"{VALIDATION_DATE_INVALID} - {VALIDATION_DATE_INVALID}"

        # Date range validation
        if entry_date > date.today():
            return False, VALIDATION_DATE_FUTURE

        if entry_date.year < 2000:
            return False, VALIDATION_DATE_TOO_OLD

        return True, None

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        # Remove spaces and check format
        clean_phone = phone.replace(" ", "")

        # French phone: minimum 10 digits
        if len(clean_phone) >= 10:
            return True

        return False

    def save(self):
        """Save employee to database."""
        # Validate form
        is_valid, error_message = self.validate()

        if not is_valid:
            self.show_error(error_message)
            return

        try:
            # Parse entry date
            entry_date_str = self.entry_date_var.get().strip()
            entry_date = datetime.strptime(entry_date_str, DATE_FORMAT).date()

            # Convert status
            status = EmployeeStatus.ACTIVE if self.status_var.get() == STATUS_ACTIVE else EmployeeStatus.INACTIVE

            if self.is_edit_mode:
                # Update existing employee
                self.employee.first_name = self.first_name_var.get().strip()
                self.employee.last_name = self.last_name_var.get().strip()
                self.employee.email = self.email_var.get().strip() or None
                self.employee.phone = self.phone_var.get().strip() or None
                self.employee.current_status = status
                self.employee.workspace = self.workspace_var.get().strip()
                self.employee.role = self.role_var.get().strip()
                self.employee.contract_type = self.contract_type_var.get()
                self.employee.entry_date = entry_date
                self.employee.updated_at = datetime.now()

                self.employee.save()

                print(f"[OK] Employee updated: {self.employee.full_name}")

            else:
                # Create new employee
                employee = Employee.create(
                    first_name=self.first_name_var.get().strip(),
                    last_name=self.last_name_var.get().strip(),
                    email=self.email_var.get().strip() or None,
                    phone=self.phone_var.get().strip() or None,
                    current_status=status,
                    workspace=self.workspace_var.get().strip(),
                    role=self.role_var.get().strip(),
                    contract_type=self.contract_type_var.get(),
                    entry_date=entry_date,
                )

                print(f"[OK] Employee created: {employee.full_name}")

                # Store result for parent
                self.result = employee

            # Close dialog
            self.destroy()

        except Exception as e:
            error_msg = f"{ERROR_SAVE_EMPLOYEE}: {e}"
            print(f"[ERROR] {error_msg}")
            self.show_error(error_msg)

    def cancel(self):
        """Cancel form editing."""
        self.result = None
        self.destroy()

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Erreur de validation", message)
        except:
            print(f"[ERROR] {message}")
