"""Contract form dialog for creating and editing employee contracts."""

from datetime import date, datetime
from typing import Optional

import customtkinter as ctk

from employee.constants import (
    CONTRACT_AMENDMENT_TYPES,
    CONTRACT_END_REASONS,
    CONTRACT_STATUS,
    CONTRACT_TYPES,
    DEFAULT_DEPARTMENTS,
    DEFAULT_POSITIONS,
    TRIAL_PERIOD_DAYS,
)
from employee.models import Contract, Employee
from utils.validation import InputValidator
from ui_ctk.constants import (
    BTN_CANCEL,
    BTN_SAVE,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    VALIDATION_DATE_INVALID,
    VALIDATION_DATE_REQUIRED,
)
from ui_ctk.forms.base_form import BaseFormDialog


class ContractFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing employee contracts.

    Features:
    - Create or edit mode
    - Support for all contract types (CDI, CDD, Interim, Alternance)
    - Automatic trial period calculation
    - Field validation
    """

    def __init__(self, parent, employee: Employee, contract: Optional[Contract] = None):
        """
        Initialize contract form dialog.

        Args:
            parent: Parent window
            employee: Employee object (required)
            contract: Contract object to edit (None for new contract)
        """
        self.employee = employee
        self.contract = contract
        self.is_edit_mode = contract is not None

        # Form variables
        self.contract_type_var = ctk.StringVar()
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        self.trial_period_end_var = ctk.StringVar()
        self.position_var = ctk.StringVar()
        self.department_var = ctk.StringVar()
        self.gross_salary_var = ctk.StringVar()
        self.weekly_hours_var = ctk.StringVar(value="35.0")
        self.document_path_var = ctk.StringVar()

        # Determine title
        if self.is_edit_mode:
            title = f"Edit Contract - {contract.contract_type}"
        else:
            title = "Add Employee Contract"

        # Initialize parent
        super().__init__(parent, title=title, width=600, height=700)

        # Track these variables for unsaved changes detection
        self.state_manager.track_variable("contract_type", self.contract_type_var)
        self.state_manager.track_variable("start_date", self.start_date_var)
        self.state_manager.track_variable("end_date", self.end_date_var)
        self.state_manager.track_variable("trial_period_end", self.trial_period_end_var)
        self.state_manager.track_variable("position", self.position_var)
        self.state_manager.track_variable("department", self.department_var)
        self.state_manager.track_variable("gross_salary", self.gross_salary_var)
        self.state_manager.track_variable("weekly_hours", self.weekly_hours_var)
        self.state_manager.track_variable("document_path", self.document_path_var)

        # Load contract data if editing
        if self.is_edit_mode:
            self.load_contract_data()

        # Bind contract type change to update UI
        self.contract_type_var.trace_add('write', self.on_contract_type_changed)

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Edit Contract" if self.is_edit_mode else "New Employee Contract"
        title_label = ctk.CTkLabel(form_frame, text=title, font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))

        # Required fields notice
        notice_label = ctk.CTkLabel(form_frame, text="* Required fields", font=("Arial", 10), text_color="gray")
        notice_label.pack(pady=(0, 10))

        # Form fields
        self.create_field_section(form_frame)

        # Buttons
        self.create_buttons(form_frame)

    def create_field_section(self, parent):
        """Create form field section."""
        # Field container
        field_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        field_container.pack(fill="both", expand=True)

        # Contract Type (required)
        type_row = ctk.CTkFrame(field_container, fg_color="transparent")
        type_row.pack(fill="x", pady=5)
        self.create_required_field_label(type_row, "Contract Type")
        self.type_dropdown = ctk.CTkOptionMenu(
            type_row,
            values=list(CONTRACT_TYPES.keys()),
            variable=self.contract_type_var,
            command=self.on_contract_type_changed,
            width=300
        )
        self.type_dropdown.pack(side="right", padx=10)

        # Start Date (required)
        start_row = ctk.CTkFrame(field_container, fg_color="transparent")
        start_row.pack(fill="x", pady=5)
        self.create_required_field_label(start_row, "Start Date")
        self.start_date_entry = ctk.CTkEntry(
            start_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.start_date_var, width=300
        )
        self.start_date_entry.pack(side="right", padx=10)

        # End Date (optional, only for CDD)
        self.end_date_row = ctk.CTkFrame(field_container, fg_color="transparent")
        self.end_date_row.pack(fill="x", pady=5)
        self.create_optional_field_label(self.end_date_row, "End Date")
        self.end_date_entry = ctk.CTkEntry(
            self.end_date_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.end_date_var, width=300
        )
        self.end_date_entry.pack(side="right", padx=10)

        # Trial Period End (optional)
        trial_row = ctk.CTkFrame(field_container, fg_color="transparent")
        trial_row.pack(fill="x", pady=5)
        self.create_optional_field_label(trial_row, "Trial Period End")
        self.trial_date_entry = ctk.CTkEntry(
            trial_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.trial_period_end_var, width=300
        )
        self.trial_date_entry.pack(side="right", padx=10)

        # Auto-calculate trial period button
        calc_trial_btn = ctk.CTkButton(trial_row, text="Auto", width=60, command=self.auto_calculate_trial)
        calc_trial_btn.pack(side="right", padx=5)

        # Position (required)
        pos_row = ctk.CTkFrame(field_container, fg_color="transparent")
        pos_row.pack(fill="x", pady=5)
        self.create_required_field_label(pos_row, "Position")
        self.pos_dropdown = ctk.CTkOptionMenu(
            pos_row, values=DEFAULT_POSITIONS, variable=self.position_var, width=300
        )
        self.pos_dropdown.pack(side="right", padx=10)

        # Department (required)
        dept_row = ctk.CTkFrame(field_container, fg_color="transparent")
        dept_row.pack(fill="x", pady=5)
        self.create_required_field_label(dept_row, "Department")
        self.dept_dropdown = ctk.CTkOptionMenu(
            dept_row, values=DEFAULT_DEPARTMENTS, variable=self.department_var, width=300
        )
        self.dept_dropdown.pack(side="right", padx=10)

        # Gross Salary (optional)
        salary_row = ctk.CTkFrame(field_container, fg_color="transparent")
        salary_row.pack(fill="x", pady=5)
        self.create_optional_field_label(salary_row, "Gross Salary (€)")
        self.salary_entry = ctk.CTkEntry(
            salary_row, placeholder_text="e.g., 2100.00", textvariable=self.gross_salary_var, width=300
        )
        self.salary_entry.pack(side="right", padx=10)

        # Weekly Hours
        hours_row = ctk.CTkFrame(field_container, fg_color="transparent")
        hours_row.pack(fill="x", pady=5)
        self.create_optional_field_label(hours_row, "Weekly Hours")
        self.hours_entry = ctk.CTkEntry(
            hours_row, placeholder_text="Default: 35.0", textvariable=self.weekly_hours_var, width=300
        )
        self.hours_entry.pack(side="right", padx=10)

        # Document Path (optional)
        doc_row = ctk.CTkFrame(field_container, fg_color="transparent")
        doc_row.pack(fill="x", pady=5)
        self.create_optional_field_label(doc_row, "Contract Document")
        doc_frame = ctk.CTkFrame(doc_row, fg_color="transparent")
        doc_frame.pack(side="right", padx=10)

        self.doc_entry = ctk.CTkEntry(
            doc_frame,
            placeholder_text="Optional - Path to contract PDF",
            textvariable=self.document_path_var,
            width=200,
        )
        self.doc_entry.pack(side="left")

        browse_btn = ctk.CTkButton(doc_frame, text="Browse...", width=80, command=self.browse_document)
        browse_btn.pack(side="left", padx=5)

        # Info text
        info_row = ctk.CTkFrame(field_container, fg_color="transparent")
        info_row.pack(fill="x", pady=(15, 5))
        self.info_label = ctk.CTkLabel(
            info_row,
            text="ℹ️ CDI: No end date | CDD: End date required",
            font=("Arial", 9),
            text_color="gray",
        )
        self.info_label.pack(padx=10)

    def create_required_field_label(self, parent, text: str):
        """Create a required field label with asterisk."""
        label = ctk.CTkLabel(parent, text=f"{text}: *", font=("Arial", 11), width=180, anchor="w")
        label.pack(side="left", padx=10)

    def create_optional_field_label(self, parent, text: str):
        """Create an optional field label."""
        label = ctk.CTkLabel(parent, text=f"{text}:", font=("Arial", 11), width=180, anchor="w")
        label.pack(side="left", padx=10)

    def create_buttons(self, parent):
        """Create form action buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(button_frame, text=BTN_CANCEL, width=120, command=self.on_cancel)
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(button_frame, text=BTN_SAVE, width=120, command=self.on_save)
        save_btn.pack(side="right", padx=5)

    def on_contract_type_changed(self, *args):
        """Handle contract type change - update end date requirement."""
        contract_type = self.contract_type_var.get()

        if contract_type == "CDI":
            # CDI has no end date
            self.info_label.configure(text="ℹ️ CDI: Permanent contract, no end date")
        elif contract_type == "CDD":
            self.info_label.configure(text="ℹ️ CDD: Fixed-term contract, end date required")
        elif contract_type == "Interim":
            self.info_label.configure(text="ℹ️ Interim: Temporary contract, end date required")
        elif contract_type == "Alternance":
            self.info_label.configure(text="ℹ️ Alternance: Apprenticeship, end date may be required")

    def auto_calculate_trial(self):
        """Auto-calculate trial period end date based on contract type."""
        contract_type = self.contract_type_var.get()
        start_date_str = self.start_date_var.get()

        if not contract_type or not start_date_str:
            return

        try:
            start_date = self.parse_date(start_date_str)
            if not start_date:
                return

            # Get trial period days for contract type
            trial_days = TRIAL_PERIOD_DAYS.get(contract_type)
            if trial_days:
                from datetime import timedelta
                trial_end = start_date + timedelta(days=trial_days)
                self.trial_period_end_var.set(trial_end.strftime(DATE_FORMAT))
        except Exception:
            pass

    def browse_document(self):
        """
        Open file browser to select contract document with security validation.

        This method:
        1. Opens file dialog for user to select a file
        2. Validates the file (extension, size, existence)
        3. Copies file to secure documents/ directory
        4. Stores the secure path in the form

        Security:
        - Prevents path traversal attacks
        - Validates file type (PDF only)
        - Limits file size (max 10MB)
        - Copies to secure storage with version tracking
        """
        try:
            from tkinter import filedialog
            import tkinter.messagebox as messagebox

            file_path = filedialog.askopenfilename(
                title="Select Contract Document PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

            if not file_path:
                return  # User cancelled

            # Validate and copy to secure storage
            from utils.file_validation import validate_and_copy_document

            success, error, secure_path = validate_and_copy_document(
                file_path,
                allowed_extensions={".pdf"},  # Only PDF for contracts
                max_size_mb=10
            )

            if not success:
                # Show error to user
                messagebox.showerror("File Validation Error", error)
                print(f"[SECURITY] File upload rejected: {error}")
                return

            # Store secure path in form
            self.document_path_var.set(secure_path)
            print(f"[OK] File validated and copied to secure storage: {secure_path}")

        except Exception as e:
            print(f"[ERROR] Failed to browse file: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Failed to select file: {e}")

    def parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse date from French format.

        Args:
            date_str: Date string in DD/MM/YYYY format

        Returns:
            date object or None if invalid
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            return None

    def load_contract_data(self):
        """Load existing contract data for editing."""
        if self.contract:
            self.contract_type_var.set(self.contract.contract_type)
            self.start_date_var.set(self.contract.start_date.strftime(DATE_FORMAT))

            if self.contract.end_date:
                self.end_date_var.set(self.contract.end_date.strftime(DATE_FORMAT))

            if self.contract.trial_period_end:
                self.trial_period_end_var.set(self.contract.trial_period_end.strftime(DATE_FORMAT))

            self.position_var.set(self.contract.position)
            self.department_var.set(self.contract.department)

            if self.contract.gross_salary:
                self.gross_salary_var.set(str(float(self.contract.gross_salary)))

            if self.contract.weekly_hours:
                self.weekly_hours_var.set(str(float(self.contract.weekly_hours)))

            if self.contract.contract_document_path:
                self.document_path_var.set(self.contract.contract_document_path)

            # Update UI based on contract type
            self.on_contract_type_changed()

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate form data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        contract_type = self.contract_type_var.get().strip()
        start_date_str = self.start_date_var.get().strip()
        end_date_str = self.end_date_var.get().strip()
        position = self.position_var.get().strip()
        department = self.department_var.get().strip()
        gross_salary_str = self.gross_salary_var.get().strip()
        weekly_hours_str = self.weekly_hours_var.get().strip()

        # Validate contract type
        if not contract_type:
            return False, "Contract type is required"

        if contract_type not in CONTRACT_TYPES:
            return False, f"Invalid contract type: {contract_type}"

        # Validate start date
        if not start_date_str:
            return False, "Start date is required"

        start_date = self.parse_date(start_date_str)
        if not start_date:
            return False, f"Start date: {VALIDATION_DATE_INVALID}"

        # Validate end date (if provided)
        end_date = None
        if end_date_str:
            end_date = self.parse_date(end_date_str)
            if not end_date:
                return False, f"End date: {VALIDATION_DATE_INVALID}"

            # End date must be after start date
            if end_date <= start_date:
                return False, "End date must be after start date"

        # For CDD and Interim, end date is required
        if contract_type in ["CDD", "Interim"] and not end_date:
            return False, f"End date is required for {contract_type} contracts"

        # Validate position
        if not position:
            return False, "Position is required"

        if position not in DEFAULT_POSITIONS:
            return False, f"Invalid position: {position}"

        # Validate department
        if not department:
            return False, "Department is required"

        if department not in DEFAULT_DEPARTMENTS:
            return False, f"Invalid department: {department}"

        # Validate gross salary (if provided)
        if gross_salary_str:
            try:
                salary = float(gross_salary_str)
                if salary <= 0:
                    return False, "Gross salary must be positive"
            except ValueError:
                return False, "Gross salary must be a valid number"

        # Validate weekly hours (if provided)
        if weekly_hours_str:
            try:
                hours = float(weekly_hours_str)
                if hours <= 0 or hours > 60:
                    return False, "Weekly hours must be between 0 and 60"
            except ValueError:
                return False, "Weekly hours must be a valid number"

        # Validate trial period end (if provided)
        trial_period_end_str = self.trial_period_end_var.get().strip()
        if trial_period_end_str:
            trial_end = self.parse_date(trial_period_end_str)
            if not trial_end:
                return False, f"Trial period end: {VALIDATION_DATE_INVALID}"

            # Trial period must be after start date
            if trial_end <= start_date:
                return False, "Trial period end must be after start date"

            # Trial period must be before end date (if exists)
            if end_date and trial_end > end_date:
                return False, "Trial period end must be before contract end date"

        return True, None

    def save(self):
        """Save form data to database."""
        contract_type = self.contract_type_var.get().strip()
        start_date_str = self.start_date_var.get().strip()
        end_date_str = self.end_date_var.get().strip() or None
        trial_period_end_str = self.trial_period_end_var.get().strip() or None
        position = self.position_var.get().strip()
        department = self.department_var.get().strip()
        gross_salary_str = self.gross_salary_var.get().strip() or None
        weekly_hours_str = self.weekly_hours_var.get().strip()
        document_path = self.document_path_var.get().strip() or None

        try:
            # Parse dates
            start_date = self.parse_date(start_date_str)
            end_date = self.parse_date(end_date_str) if end_date_str else None
            trial_period_end = self.parse_date(trial_period_end_str) if trial_period_end_str else None

            # Parse salary and hours
            gross_salary = float(gross_salary_str) if gross_salary_str else None
            weekly_hours = float(weekly_hours_str) if weekly_hours_str else 35.0

            # Determine status
            status = CONTRACT_STATUS.ACTIVE

            if self.is_edit_mode:
                # Update existing contract
                self.contract.contract_type = contract_type
                self.contract.start_date = start_date
                self.contract.end_date = end_date
                self.contract.trial_period_end = trial_period_end
                self.contract.position = position
                self.contract.department = department
                self.contract.gross_salary = gross_salary
                self.contract.weekly_hours = weekly_hours
                self.contract.status = status
                self.contract.contract_document_path = document_path
                self.contract.save()
                print(f"[OK] Contract updated: {contract_type} for {self.employee.full_name}")
            else:
                # Create new contract
                self.contract = Contract.create(
                    employee=self.employee,
                    contract_type=contract_type,
                    start_date=start_date,
                    end_date=end_date,
                    trial_period_end=trial_period_end,
                    position=position,
                    department=department,
                    gross_salary=gross_salary,
                    weekly_hours=weekly_hours,
                    status=status,
                    contract_document_path=document_path,
                )
                print(f"[OK] Contract created: {contract_type} for {self.employee.full_name}")

        except Exception as e:
            error_msg = f"Error saving contract: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.show_error(error_msg)
            raise
