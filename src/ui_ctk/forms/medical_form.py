"""Medical visit form dialog for creating and editing medical visits."""

from datetime import date, datetime
from typing import Optional

import customtkinter as ctk

from employee.models import MedicalVisit
from ui_ctk.constants import (
    BTN_CANCEL,
    BTN_SAVE,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    ERROR_SAVE_VISIT,
    FORM_MEDICAL_DATE,
    FORM_MEDICAL_DOCUMENT,
    FORM_MEDICAL_EXPIRATION_DATE,
    FORM_MEDICAL_RESULT,
    FORM_MEDICAL_TYPE,
    VALIDATION_DATE_INVALID,
    VALIDATION_DATE_REQUIRED,
    VISIT_RESULT_CHOICES,
    VISIT_RESULTS,
    VISIT_TYPE_CHOICES,
    VISIT_TYPES,
)
from ui_ctk.forms.base_form import BaseFormDialog


class MedicalVisitFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing medical visits.

    Features:
    - Create or edit mode
    - Automatic expiration date calculation based on visit type
    - Field validation
    - Optional document path
    """

    def __init__(self, parent, employee, visit: Optional[MedicalVisit] = None):
        """
        Initialize medical visit form dialog.

        Args:
            parent: Parent window
            employee: Employee object (required)
            visit: MedicalVisit object to edit (None for new visit)
        """
        self.employee = employee
        self.visit = visit
        self.is_edit_mode = visit is not None

        # Form variables
        self.visit_type_var = ctk.StringVar()
        self.visit_date_var = ctk.StringVar()
        self.result_var = ctk.StringVar()
        self.document_path_var = ctk.StringVar()
        self.expiration_display_var = ctk.StringVar()  # For display only

        # Determine title
        if self.is_edit_mode:
            title = f"Edit Medical Visit - {VISIT_TYPES.get(visit.visit_type, visit.visit_type)}"
        else:
            title = "Add Medical Visit"

        # Initialize parent
        super().__init__(parent, title=title, width=550, height=500)

        # Load visit data if editing
        if self.is_edit_mode:
            self.load_visit_data()

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Edit Medical Visit" if self.is_edit_mode else "New Medical Visit"
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
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.pack(fill="both", expand=True)

        # Visit Type (required)
        type_row = ctk.CTkFrame(field_container, fg_color="transparent")
        type_row.pack(fill="x", pady=5)
        self.create_required_field_label(type_row, FORM_MEDICAL_TYPE)

        # Create French labels dropdown
        type_labels = [VISIT_TYPES[t] for t in VISIT_TYPE_CHOICES]
        self.type_dropdown = ctk.CTkOptionMenu(type_row, values=type_labels, command=self.on_type_changed, width=300)
        self.type_dropdown.pack(side="right", padx=10)

        # Visit Date (required)
        date_row = ctk.CTkFrame(field_container, fg_color="transparent")
        date_row.pack(fill="x", pady=5)
        self.create_required_field_label(date_row, FORM_MEDICAL_DATE)
        self.date_entry = ctk.CTkEntry(
            date_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.visit_date_var, width=300
        )
        self.date_entry.pack(side="right", padx=10)

        # Result (required)
        result_row = ctk.CTkFrame(field_container, fg_color="transparent")
        result_row.pack(fill="x", pady=5)
        self.create_required_field_label(result_row, FORM_MEDICAL_RESULT)

        # Create French labels dropdown
        result_labels = [VISIT_RESULTS[r] for r in VISIT_RESULT_CHOICES]
        self.result_dropdown = ctk.CTkOptionMenu(result_row, values=result_labels, width=300)
        self.result_dropdown.pack(side="right", padx=10)

        # Expiration Date (display only, calculated)
        exp_row = ctk.CTkFrame(field_container, fg_color="transparent")
        exp_row.pack(fill="x", pady=5)
        exp_label = ctk.CTkLabel(
            exp_row,
            text=f"{FORM_MEDICAL_EXPIRATION_DATE} (auto-calculated):",
            font=("Arial", 11),
            width=280,
            anchor="w",
        )
        exp_label.pack(side="left", padx=10)

        self.expiration_label = ctk.CTkLabel(
            exp_row, text="Select type and date first", font=("Arial", 11), text_color="gray"
        )
        self.expiration_label.pack(side="left", padx=10)

        # Document Path (optional)
        doc_row = ctk.CTkFrame(field_container, fg_color="transparent")
        doc_row.pack(fill="x", pady=5)
        doc_label = ctk.CTkLabel(doc_row, text=f"{FORM_MEDICAL_DOCUMENT}:", font=("Arial", 11), width=180, anchor="w")
        doc_label.pack(side="left", padx=10)

        doc_frame = ctk.CTkFrame(doc_row, fg_color="transparent")
        doc_frame.pack(side="right", padx=10)

        self.doc_entry = ctk.CTkEntry(
            doc_frame,
            placeholder_text="Optional - Path to certificate PDF",
            textvariable=self.document_path_var,
            width=200,
        )
        self.doc_entry.pack(side="left")

        browse_btn = ctk.CTkButton(doc_frame, text="Browse...", width=80, command=self.browse_document)
        browse_btn.pack(side="left", padx=5)

        # Info text
        info_row = ctk.CTkFrame(field_container, fg_color="transparent")
        info_row.pack(fill="x", pady=(15, 5))
        info_text = ctk.CTkLabel(
            info_row,
            text="ℹ️ Initial/Periodic: 2 years validity | Recovery: 1 year validity",
            font=("Arial", 9),
            text_color="gray",
        )
        info_text.pack(padx=10)

    def create_required_field_label(self, parent, text: str):
        """Create a required field label with asterisk."""
        label = ctk.CTkLabel(parent, text=f"{text}: *", font=("Arial", 11), width=180, anchor="w")
        label.pack(side="left", padx=10)

    def create_buttons(self, parent):
        """Create form action buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(button_frame, text=BTN_CANCEL, width=120, command=self.on_cancel)
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(button_frame, text=BTN_SAVE, width=120, command=self.on_save)
        save_btn.pack(side="right", padx=5)

    def on_type_changed(self, value):
        """Handle visit type change - update expiration date preview."""
        self.update_expiration_preview()

    def update_expiration_preview(self):
        """Update the expiration date preview based on selection."""
        type_label = self.type_dropdown.get()
        date_str = self.visit_date_var.get()

        if type_label and date_str:
            try:
                # Convert French label back to type key
                visit_type = self._get_type_key_from_label(type_label)

                visit_date = self.parse_date(date_str)
                if visit_date:
                    expiration = MedicalVisit.calculate_expiration(visit_type, visit_date)
                    self.expiration_label.configure(text=expiration.strftime(DATE_FORMAT), text_color="black")
                    return
            except Exception:
                pass

        self.expiration_label.configure(text="Select type and date first", text_color="gray")

    def _get_type_key_from_label(self, label: str) -> str:
        """Convert French label back to visit type key."""
        for key, value in VISIT_TYPES.items():
            if value == label:
                return key
        return label

    def _get_result_key_from_label(self, label: str) -> str:
        """Convert French label back to result key."""
        for key, value in VISIT_RESULTS.items():
            if value == label:
                return key
        return label

    def browse_document(self):
        """Open file browser to select document."""
        try:
            from tkinter import filedialog

            file_path = filedialog.askopenfilename(
                title="Select Medical Certificate PDF", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                self.document_path_var.set(file_path)
        except Exception as e:
            print(f"[ERROR] Failed to browse file: {e}")

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

    def load_visit_data(self):
        """Load existing visit data for editing."""
        if self.visit:
            # Set visit type by French label
            type_label = VISIT_TYPES.get(self.visit.visit_type, self.visit.visit_type)
            self.type_dropdown.set(type_label)
            self.visit_type_var.set(self.visit.visit_type)

            self.visit_date_var.set(self.visit.visit_date.strftime(DATE_FORMAT))

            # Set result by French label
            result_label = VISIT_RESULTS.get(self.visit.result, self.visit.result)
            self.result_dropdown.set(result_label)
            self.result_var.set(self.visit.result)

            self.document_path_var.set(self.visit.document_path or "")
            self.update_expiration_preview()

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate form data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        type_label = self.type_dropdown.get()
        date_str = self.visit_date_var.get().strip()
        result_label = self.result_dropdown.get()

        # Validate visit type
        if not type_label:
            return False, f"{FORM_MEDICAL_TYPE} is required"

        visit_type = self._get_type_key_from_label(type_label)
        if visit_type not in VISIT_TYPE_CHOICES:
            return False, f"Invalid {FORM_MEDICAL_TYPE}"

        # Validate visit date
        if not date_str:
            return False, VALIDATION_DATE_REQUIRED

        visit_date = self.parse_date(date_str)
        if not visit_date:
            return False, VALIDATION_DATE_INVALID

        # Check if date is reasonable
        today = date.today()
        if visit_date > today:
            # Allow future dates up to 1 month (for scheduled visits)
            if (visit_date - today).days > 30:
                return False, "Visit date cannot be more than 1 month in the future"
        elif visit_date.year < 2000:
            return False, "Visit date seems incorrect (before 2000)"

        # Validate result
        if not result_label:
            return False, f"{FORM_MEDICAL_RESULT} is required"

        result = self._get_result_key_from_label(result_label)
        if result not in VISIT_RESULT_CHOICES:
            return False, f"Invalid {FORM_MEDICAL_RESULT}"

        return True, None

    def save(self):
        """Save form data to database."""
        type_label = self.type_dropdown.get()
        date_str = self.visit_date_var.get().strip()
        result_label = self.result_dropdown.get()
        document_path = self.document_path_var.get().strip() or None

        # Convert labels to keys
        visit_type = self._get_type_key_from_label(type_label)
        result = self._get_result_key_from_label(result_label)

        # Parse visit date
        visit_date = self.parse_date(date_str)

        # Calculate expiration date
        expiration_date = MedicalVisit.calculate_expiration(visit_type, visit_date)

        try:
            if self.is_edit_mode:
                # Update existing visit
                self.visit.visit_type = visit_type
                self.visit.visit_date = visit_date
                self.visit.expiration_date = expiration_date
                self.visit.result = result
                self.visit.document_path = document_path
                self.visit.save()
                print(f"[OK] Medical visit updated: {visit_type} for {self.employee.full_name}")
            else:
                # Create new visit
                self.visit = MedicalVisit.create(
                    employee=self.employee,
                    visit_type=visit_type,
                    visit_date=visit_date,
                    expiration_date=expiration_date,
                    result=result,
                    document_path=document_path,
                )
                print(f"[OK] Medical visit created: {visit_type} for {self.employee.full_name}")

        except Exception as e:
            raise Exception(f"{ERROR_SAVE_VISIT}: {str(e)}")
