"""Employee detail view with certifications and visits."""

from datetime import date

import customtkinter as ctk

from employee.models import Caces, Employee, MedicalVisit
from ui_ctk.constants import (
    BTN_ADD,
    BTN_BACK,
    BTN_DELETE,
    BTN_EDIT,
    COLOR_CRITICAL,
    COLOR_INACTIVE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    CONFIRM_DELETE_CACES,
    CONFIRM_DELETE_EMPLOYEE,
    CONFIRM_DELETE_VISIT,
    CONFIRM_DELETE_WARNING,
    DATE_FORMAT,
    EMPTY_NO_CACES,
    EMPTY_NO_VISITS,
    ERROR_DELETE_CACES,
    ERROR_DELETE_EMPLOYEE,
    ERROR_DELETE_VISIT,
    EXPIRATION_STATUS_EXPIRED,
    EXPIRATION_STATUS_SOON,
    EXPIRATION_STATUS_URGENT,
    EXPIRATION_STATUS_VALID,
    SECTION_CACES,
    SECTION_INFO,
    SECTION_MEDICAL,
    SECTION_TRAININGS,
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    VISIT_TYPES,
)
from ui_ctk.views.base_view import BaseView


class EmployeeDetailView(BaseView):
    """
    Detailed view of a single employee.

    Features:
    - Display all employee information
    - Show CACES certifications with status
    - Show medical visits with expiration
    - Edit employee button
    - Delete employee button
    - Back to list button
    """

    def __init__(self, master, employee: Employee, title: str = ""):
        """
        Initialize employee detail view.

        Args:
            master: Parent window
            employee: Employee object to display
            title: View title
        """
        self.employee = employee

        # Call parent WITHOUT title to avoid creating default header
        super().__init__(master, title="")

        # Create UI (header with buttons + content)
        self.create_header()
        self.create_content()

    def create_header(self):
        """Create view header with back button."""
        # Header frame
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)

        # Back button
        back_btn = ctk.CTkButton(header_frame, text=f"← {BTN_BACK}", width=100, command=self.go_back)
        back_btn.pack(side="left", padx=10)

        # Employee name
        name_label = ctk.CTkLabel(header_frame, text=self.employee.full_name, font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=20)

        # Status badge
        status_text = STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE
        status_color = COLOR_SUCCESS if self.employee.is_active else COLOR_INACTIVE
        status_label = ctk.CTkLabel(header_frame, text=status_text, font=("Arial", 12, "bold"), text_color=status_color)
        status_label.pack(side="left", padx=10)

        # Action buttons
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(action_frame, text=f"✏️ {BTN_EDIT}", width=120, command=self.edit_employee)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            action_frame, text=f"🗑️ {BTN_DELETE}", width=120, command=self.delete_employee, fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=5)

    def create_content(self):
        """Create content sections."""
        # Scrollable content
        content = ctk.CTkScrollableFrame(self)
        content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Information section
        self.create_info_section(content)

        # CACES section
        self.create_caces_section(content)

        # Medical visits section
        self.create_medical_section(content)

        # Online trainings section (placeholder for future)
        self.create_trainings_section(content)

    def create_info_section(self, parent):
        """Create employee information section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(10, 5))

        # Section header
        header = ctk.CTkLabel(section, text=f"👤 {SECTION_INFO}", font=("Arial", 14, "bold"))
        header.pack(pady=10, padx=10, anchor="w")

        # Info grid
        info_frame = ctk.CTkFrame(section, fg_color=("gray90", "gray20"))
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Info rows
        self.create_info_row(info_frame, "Email:", self.employee.email or "-")
        self.create_info_row(info_frame, "Téléphone:", self.employee.phone or "-")
        self.create_info_row(info_frame, "Statut:", STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE)
        self.create_info_row(info_frame, "Zone de travail:", self.employee.workspace)
        self.create_info_row(info_frame, "Poste:", self.employee.role)
        self.create_info_row(info_frame, "Type de contrat:", self.employee.contract_type)

        # Entry date
        entry_date_str = self.employee.entry_date.strftime(DATE_FORMAT)
        self.create_info_row(info_frame, "Date d'entrée:", entry_date_str)

        # Seniority
        seniority_years = self.employee.seniority
        seniority_text = f"{seniority_years} an(s)"
        self.create_info_row(info_frame, "Ancienneté:", seniority_text)

    def create_info_row(self, parent, label: str, value: str):
        """Create a single info row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)

        # Label
        label_widget = ctk.CTkLabel(row, text=label, font=("Arial", 11), anchor="w", width=150)
        label_widget.pack(side="left", padx=10)

        # Value
        value_widget = ctk.CTkLabel(row, text=value, font=("Arial", 11), anchor="w")
        value_widget.pack(side="left", padx=10)

    def create_caces_section(self, parent):
        """Create CACES certifications section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text=f"🔧 {SECTION_CACES}", font=("Arial", 14, "bold"))
        header.pack(side="left")

        add_btn = ctk.CTkButton(header_frame, text=f"+ {BTN_ADD}", width=100, command=self.add_caces)
        add_btn.pack(side="right")

        # Load CACES
        caces_list = list(Caces.select().where(Caces.employee == self.employee))

        if caces_list:
            # Display CACES
            for caces in caces_list:
                self.create_caces_item(section, caces)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(section, text=EMPTY_NO_CACES, text_color="gray")
            empty_label.pack(padx=10, pady=(0, 10))

    def create_caces_item(self, parent, caces: Caces):
        """Create a single CACES item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Type and date
        type_label = ctk.CTkLabel(item, text=f"{caces.kind}", font=("Arial", 12, "bold"), anchor="w")
        type_label.pack(side="left", padx=10, pady=5)

        # Expiration info
        expiration_text = f"Expire le {caces.expiration_date.strftime(DATE_FORMAT)}"
        expiration_label = ctk.CTkLabel(item, text=expiration_text, font=("Arial", 11), anchor="w")
        expiration_label.pack(side="left", padx=10)

        # Status badge
        days_until = (caces.expiration_date - date.today()).days
        if days_until < 0:
            status_text = f"{EXPIRATION_STATUS_EXPIRED}"
            status_color = COLOR_CRITICAL
        elif days_until < 30:
            status_text = f"{EXPIRATION_STATUS_URGENT} ({days_until}j)"
            status_color = COLOR_CRITICAL
        elif days_until < 90:
            status_text = f"{EXPIRATION_STATUS_SOON} ({days_until}j)"
            status_color = COLOR_WARNING
        else:
            status_text = EXPIRATION_STATUS_VALID
            status_color = COLOR_SUCCESS

        status_label = ctk.CTkLabel(item, text=status_text, font=("Arial", 10, "bold"), text_color=status_color)
        status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(action_frame, text="✏️", width=40, command=lambda: self.edit_caces(caces))
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            action_frame, text="🗑️", width=40, command=lambda: self.delete_caces(caces), fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=2)

    def create_medical_section(self, parent):
        """Create medical visits section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text=f"🏥 {SECTION_MEDICAL}", font=("Arial", 14, "bold"))
        header.pack(side="left")

        add_btn = ctk.CTkButton(header_frame, text=f"+ {BTN_ADD}", width=100, command=self.add_medical_visit)
        add_btn.pack(side="right")

        # Load visits
        visits = list(MedicalVisit.select().where(MedicalVisit.employee == self.employee))

        if visits:
            # Display visits
            for visit in visits:
                self.create_medical_item(section, visit)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(section, text=EMPTY_NO_VISITS, text_color="gray")
            empty_label.pack(padx=10, pady=(0, 10))

    def create_medical_item(self, parent, visit: MedicalVisit):
        """Create a single medical visit item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Type and date
        type_label = ctk.CTkLabel(item, text=f"{visit.visit_type}", font=("Arial", 12, "bold"), anchor="w")
        type_label.pack(side="left", padx=10, pady=5)

        # Date
        date_text = f"Visite du {visit.visit_date.strftime(DATE_FORMAT)}"
        date_label = ctk.CTkLabel(item, text=date_text, font=("Arial", 11), anchor="w")
        date_label.pack(side="left", padx=10)

        # Expiration information
        if visit.expiration_date:
            exp_text = f"Expiration: {visit.expiration_date.strftime(DATE_FORMAT)}"
            exp_label = ctk.CTkLabel(item, text=exp_text, font=("Arial", 11), anchor="w")
            exp_label.pack(side="left", padx=10)

            # Status badge based on expiration
            days_until = (visit.expiration_date - date.today()).days
            if days_until < 0:
                status_text = EXPIRATION_STATUS_EXPIRED
                status_color = COLOR_CRITICAL
            elif days_until < 30:
                status_text = f"{EXPIRATION_STATUS_URGENT} ({days_until}j)"
                status_color = COLOR_CRITICAL
            elif days_until < 90:
                status_text = f"{EXPIRATION_STATUS_SOON} ({days_until}j)"
                status_color = COLOR_WARNING
            else:
                status_text = EXPIRATION_STATUS_VALID
                status_color = COLOR_SUCCESS

            status_label = ctk.CTkLabel(item, text=status_text, font=("Arial", 10, "bold"), text_color=status_color)
            status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(action_frame, text="✏️", width=40, command=lambda: self.edit_medical_visit(visit))
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            action_frame, text="🗑️", width=40, command=lambda: self.delete_medical_visit(visit), fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=2)

    def create_trainings_section(self, parent):
        """Create online trainings section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text=f"📚 {SECTION_TRAININGS}", font=("Arial", 14, "bold"))
        header.pack(side="left")

        # Placeholder for future implementation
        placeholder_label = ctk.CTkLabel(section, text="Fonctionnalité à venir", text_color="gray")
        placeholder_label.pack(padx=10, pady=(0, 10))

    # ===== Action Methods =====

    def go_back(self):
        """Navigate back to employee list."""
        try:
            main_window = self.master_window
            from ui_ctk.views.employee_list import EmployeeListView

            main_window.switch_view(EmployeeListView, title="Liste des Employés")

        except Exception as e:
            print(f"[ERROR] Failed to go back: {e}")

    def edit_employee(self):
        """Open employee edit form."""
        try:
            from ui_ctk.forms.employee_form import EmployeeFormDialog

            dialog = EmployeeFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data
                self.employee = Employee.get_by_id(self.employee.id)
                # Refresh view
                self.destroy()
                # Recreate with updated data
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to edit employee: {e}")
            self.show_error(f"Failed to edit employee: {e}")

    def delete_employee(self):
        """Delete employee after confirmation."""
        try:
            import tkinter.messagebox as messagebox

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirmer la suppression", f"{CONFIRM_DELETE_EMPLOYEE}\n\n{CONFIRM_DELETE_WARNING}"
            )

            if confirm:
                # Delete employee
                self.employee.delete_instance()

                print(f"[OK] Employee deleted: {self.employee.full_name}")

                # Go back to list
                self.go_back()

        except Exception as e:
            print(f"[ERROR] Failed to delete employee: {e}")
            self.show_error(f"{ERROR_DELETE_EMPLOYEE}: {e}")

    def refresh_view(self):
        """Reload employee data and recreate the view."""
        try:
            # Reload employee data
            self.employee = Employee.get_by_id(self.employee.id)

            # Use MainWindow's switch_view to properly recreate the view
            if self.master_window:
                self.master_window.switch_view(EmployeeDetailView, employee=self.employee)
            else:
                # Fallback: manual recreation (shouldn't happen)
                print("[WARN] master_window not found, using manual refresh")
                # Just destroy current view, don't recreate (will be handled by parent)
                self.destroy()

        except Exception as e:
            print(f"[ERROR] Failed to refresh view: {e}")

    def add_caces(self):
        """Add new CACES certification."""
        try:
            from ui_ctk.forms.caces_form import CacesFormDialog

            dialog = CacesFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data and refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to add CACES: {e}")
            self.show_error(f"Failed to add CACES: {e}")

    def edit_caces(self, caces: Caces):
        """Edit existing CACES certification."""
        try:
            from ui_ctk.forms.caces_form import CacesFormDialog

            dialog = CacesFormDialog(self, employee=self.employee, caces=caces)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data and refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to edit CACES: {e}")
            self.show_error(f"Failed to edit CACES: {e}")

    def delete_caces(self, caces: Caces):
        """Delete CACES certification."""
        try:
            import tkinter.messagebox as messagebox

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Deletion", f"{CONFIRM_DELETE_CACES}\n\nType: {caces.kind}\nEmployee: {self.employee.full_name}"
            )

            if confirm:
                # Delete CACES
                caces.delete_instance()
                print(f"[OK] CACES deleted: {caces.kind}")

                # Refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to delete CACES: {e}")
            self.show_error(f"{ERROR_DELETE_CACES}: {e}")

    def add_medical_visit(self):
        """Add new medical visit."""
        try:
            from ui_ctk.forms.medical_form import MedicalVisitFormDialog

            dialog = MedicalVisitFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data and refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to add medical visit: {e}")
            self.show_error(f"Failed to add medical visit: {e}")

    def edit_medical_visit(self, visit: MedicalVisit):
        """Edit existing medical visit."""
        try:
            from ui_ctk.forms.medical_form import MedicalVisitFormDialog

            dialog = MedicalVisitFormDialog(self, employee=self.employee, visit=visit)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data and refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to edit medical visit: {e}")
            self.show_error(f"Failed to edit medical visit: {e}")

    def delete_medical_visit(self, visit: MedicalVisit):
        """Delete medical visit."""
        try:
            import tkinter.messagebox as messagebox

            # Get French label for visit type
            visit_type_label = VISIT_TYPES.get(visit.visit_type, visit.visit_type)

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"{CONFIRM_DELETE_VISIT}\n\nType: {visit_type_label}\nDate: {visit.visit_date.strftime(DATE_FORMAT)}\nEmployee: {self.employee.full_name}",
            )

            if confirm:
                # Delete visit
                visit.delete_instance()
                print(f"[OK] Medical visit deleted: {visit_type_label}")

                # Refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to delete medical visit: {e}")
            self.show_error(f"{ERROR_DELETE_VISIT}: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Erreur", message)
        except:
            print(f"[ERROR] {message}")

    def show_info(self, message: str):
        """Show info message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showinfo("Information", message)
        except:
            print(f"[INFO] {message}")
