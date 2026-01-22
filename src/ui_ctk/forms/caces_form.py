"""CACES certification form dialog for creating and editing certifications."""

from datetime import date, datetime
from typing import Optional

import customtkinter as ctk

from employee.models import Caces
from ui_ctk.constants import (
    BTN_CANCEL,
    BTN_SAVE,
    CACES_TYPES,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    ERROR_SAVE_CACES,
    FORM_CACES_COMPLETION_DATE,
    FORM_CACES_DOCUMENT,
    FORM_CACES_TYPE,
    VALIDATION_DATE_INVALID,
    VALIDATION_DATE_REQUIRED,
)
from ui_ctk.forms.base_form import BaseFormDialog


class CacesFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing CACES certifications.

    Features:
    - Create or edit mode
    - Automatic expiration date calculation based on CACES type
    - Field validation
    - Optional document path
    """

    def __init__(self, parent, employee, caces: Optional[Caces] = None):
        """
        Initialize CACES form dialog.

        Args:
            parent: Parent window
            employee: Employee object (required)
            caces: Caces object to edit (None for new certification)
        """
        self.employee = employee
        self.caces = caces
        self.is_edit_mode = caces is not None

        # Form variables
        self.kind_var = ctk.StringVar()
        self.completion_date_var = ctk.StringVar()
        self.document_path_var = ctk.StringVar()
        self.expiration_display_var = ctk.StringVar()  # For display only

        # Determine title
        if self.is_edit_mode:
            title = f"Edit CACES - {caces.kind}"
        else:
            title = "Add CACES Certification"

        # Initialize parent
        super().__init__(parent, title=title, width=500, height=450)

        # Load CACES data if editing
        if self.is_edit_mode:
            self.load_caces_data()

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Edit CACES Certification" if self.is_edit_mode else "New CACES Certification"
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

        # CACES Type (required)
        type_row = ctk.CTkFrame(field_container, fg_color="transparent")
        type_row.pack(fill="x", pady=5)
        self.create_required_field_label(type_row, FORM_CACES_TYPE)
        self.kind_dropdown = ctk.CTkOptionMenu(
            type_row, values=CACES_TYPES, variable=self.kind_var, command=self.on_kind_changed, width=300
        )
        self.kind_dropdown.pack(side="right", padx=10)

        # Completion Date (required)
        date_row = ctk.CTkFrame(field_container, fg_color="transparent")
        date_row.pack(fill="x", pady=5)
        self.create_required_field_label(date_row, FORM_CACES_COMPLETION_DATE)
        self.date_entry = ctk.CTkEntry(
            date_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.completion_date_var, width=300
        )
        self.date_entry.pack(side="right", padx=10)

        # Expiration Date (display only, calculated)
        exp_row = ctk.CTkFrame(field_container, fg_color="transparent")
        exp_row.pack(fill="x", pady=5)
        exp_label = ctk.CTkLabel(
            exp_row, text="Expiration Date (auto-calculated):", font=("Arial", 11), width=180, anchor="w"
        )
        exp_label.pack(side="left", padx=10)

        self.expiration_label = ctk.CTkLabel(
            exp_row, text="Select type and date first", font=("Arial", 11), text_color="gray"
        )
        self.expiration_label.pack(side="left", padx=10)

        # Document Path (optional)
        doc_row = ctk.CTkFrame(field_container, fg_color="transparent")
        doc_row.pack(fill="x", pady=5)
        doc_label = ctk.CTkLabel(doc_row, text=f"{FORM_CACES_DOCUMENT}:", font=("Arial", 11), width=180, anchor="w")
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
            text="ℹ️ R489-1A/1B/3/4: 5 years validity | R489-5: 10 years validity",
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

    def on_kind_changed(self, value):
        """Handle CACES type change - update expiration date preview."""
        self.update_expiration_preview()

    def update_expiration_preview(self):
        """Update the expiration date preview based on selection."""
        kind = self.kind_var.get()
        date_str = self.completion_date_var.get()

        if kind and date_str:
            try:
                completion_date = self.parse_date(date_str)
                if completion_date:
                    expiration = Caces.calculate_expiration(kind, completion_date)
                    self.expiration_label.configure(text=expiration.strftime(DATE_FORMAT), text_color="black")
                    return
            except Exception:
                pass

        self.expiration_label.configure(text="Select type and date first", text_color="gray")

    def browse_document(self):
        """Open file browser to select document."""
        try:
            from tkinter import filedialog

            file_path = filedialog.askopenfilename(
                title="Select CACES Certificate PDF", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
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

    def load_caces_data(self):
        """Load existing CACES data for editing."""
        if self.caces:
            self.kind_var.set(self.caces.kind)
            self.completion_date_var.set(self.caces.completion_date.strftime(DATE_FORMAT))
            self.document_path_var.set(self.caces.document_path or "")
            self.update_expiration_preview()

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate form data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        kind = self.kind_var.get().strip()
        completion_str = self.completion_date_var.get().strip()

        # Validate kind
        if not kind:
            return False, f"{FORM_CACES_TYPE} is required"

        if kind not in CACES_TYPES:
            return False, f"Invalid {FORM_CACES_TYPE}"

        # Validate completion date
        if not completion_str:
            return False, VALIDATION_DATE_REQUIRED

        completion_date = self.parse_date(completion_str)
        if not completion_date:
            return False, VALIDATION_DATE_INVALID

        # Check if date is reasonable (not too far in the past or future)
        today = date.today()
        if completion_date > today:
            # Allow future dates up to 1 month (for upcoming certifications)
            if (completion_date - today).days > 30:
                return False, "Completion date cannot be more than 1 month in the future"
        elif completion_date.year < 2000:
            return False, "Completion date seems incorrect (before 2000)"

        return True, None

    def save(self):
        """Save form data to database."""
        kind = self.kind_var.get().strip()
        completion_str = self.completion_date_var.get().strip()
        document_path = self.document_path_var.get().strip() or None

        # Parse completion date
        completion_date = self.parse_date(completion_str)

        # Calculate expiration date
        expiration_date = Caces.calculate_expiration(kind, completion_date)

        try:
            if self.is_edit_mode:
                # Update existing CACES
                self.caces.kind = kind
                self.caces.completion_date = completion_date
                self.caces.expiration_date = expiration_date
                self.caces.document_path = document_path
                self.caces.save()
                print(f"[OK] CACES updated: {kind} for {self.employee.full_name}")
            else:
                # Create new CACES
                self.caces = Caces.create(
                    employee=self.employee,
                    kind=kind,
                    completion_date=completion_date,
                    expiration_date=expiration_date,
                    document_path=document_path,
                )
                print(f"[OK] CACES created: {kind} for {self.employee.full_name}")

        except Exception as e:
            raise Exception(f"{ERROR_SAVE_CACES}: {str(e)}")
