"""Employee form view - Add/Edit employee form."""

import flet as ft
from datetime import date
from typing import Optional

from ui.controllers.employee_controller import EmployeeController
from ui.widgets.forms import (
    TextFormField,
    DropdownField,
    FormSection,
)
from employee.constants import EmployeeStatus, ContractType


class EmployeeFormView:
    """
    Employee form view for adding and editing employees.

    Supports both create and update modes with validation.
    """

    def __init__(self, page: ft.Page, employee_id: Optional[str] = None):
        """
        Initialize employee form view.

        Args:
            page: The Flet page instance
            employee_id: Employee UUID for edit mode, None for create mode
        """
        self.page = page
        self.employee_id = employee_id
        self.controller = EmployeeController()
        self.is_edit_mode = (employee_id is not None)

        # Form field references
        self.first_name_field = None
        self.last_name_field = None
        self.external_id_field = None
        self.status_field = None
        self.workspace_field = None
        self.role_field = None
        self.contract_type_field = None
        self.entry_date_field = None

    def build(self) -> ft.Column:
        """
        Build the employee form view.

        Returns:
            ft.Column containing form sections
        """
        title = "Edit Employee" if self.is_edit_mode else "Add Employee"

        # Build form sections
        header = self._build_header(title)
        basic_info_section = self._build_basic_info_section()
        employment_section = self._build_employment_section()
        actions_section = self._build_actions()

        # Assemble form
        return ft.Column(
            [
                header,
                ft.Container(height=20),
                basic_info_section,
                ft.Container(height=20),
                employment_section,
                ft.Container(height=20),
                actions_section,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_header(self, title: str) -> ft.Row:
        """Build form header with back button."""
        return ft.Row(
            [
                ft.IconButton(
                    ft.icons.CHEVRON_LEFT,
                    on_click=lambda e: self._navigate_back(),
                ),
                ft.Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

    def _build_basic_info_section(self) -> FormSection:
        """Build basic information form section."""
        self.first_name_field = TextFormField(
            "First Name",
            required=True,
            hint_text="Enter first name",
        )

        self.last_name_field = TextFormField(
            "Last Name",
            required=True,
            hint_text="Enter last name",
        )

        self.external_id_field = TextFormField(
            "External ID",
            hint_text="WMS reference (optional)",
        )

        return FormSection(
            "Basic Information",
            [
                self.first_name_field,
                self.last_name_field,
                self.external_id_field,
            ],
        )

    def _build_employment_section(self) -> FormSection:
        """Build employment details form section."""
        # Status options
        status_options = [
            (EmployeeStatus.ACTIVE, "Active"),
            (EmployeeStatus.INACTIVE, "Inactive"),
        ]

        self.status_field = DropdownField(
            "Status",
            options=status_options,
            value=EmployeeStatus.ACTIVE,
            required=True,
        )

        # Workspace options (should be dynamic from config)
        workspace_options = [
            ("Quai", "Quai"),
            ("Bureau", "Bureau"),
            ("Magasin", "Magasin"),
            ("Atelier", "Atelier"),
        ]

        self.workspace_field = DropdownField(
            "Workspace",
            options=workspace_options,
            required=True,
        )

        # Role options (should be dynamic from config)
        role_options = [
            ("Préparateur", "Préparateur de commandes"),
            ("Cariste", "Cariste"),
            ("Magasinier", "Magasinier"),
            ("Réceptionnaire", "Réceptionnaire"),
            ("Manager", "Manager"),
            ("Administratif", "Administratif"),
        ]

        self.role_field = DropdownField(
            "Role",
            options=role_options,
            required=True,
        )

        # Contract type options
        contract_options = [
            (ContractType.CDI, "CDI"),
            (ContractType.CDD, "CDD"),
            (ContractType.INTERIM, "Interim"),
            (ContractType.ALTERNANCE, "Alternance"),
        ]

        self.contract_type_field = DropdownField(
            "Contract Type",
            options=contract_options,
            required=True,
        )

        # Entry date (simplified - use text input for now)
        self.entry_date_field = TextFormField(
            "Entry Date",
            required=True,
            hint_text="DD/MM/YYYY (e.g., 15/01/2020)",
        )

        return FormSection(
            "Employment Details",
            [
                self.status_field,
                self.workspace_field,
                self.role_field,
                self.contract_type_field,
                self.entry_date_field,
            ],
        )

    def _build_actions(self) -> ft.Row:
        """Build form action buttons."""
        return ft.Row(
            [
                ft.ElevatedButton(
                    "💾 Save",
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self._save_employee(),
                ),
                ft.ElevatedButton(
                    "❌ Cancel",
                    bgcolor=ft.Colors.GREY,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self._navigate_back(),
                ),
            ],
            spacing=10,
        )

    def _validate_form(self) -> tuple[bool, Optional[str]]:
        """
        Validate form fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        if not self.first_name_field.value.strip():
            return False, "First name is required"

        if not self.last_name_field.value.strip():
            return False, "Last name is required"

        if not self.status_field.value:
            return False, "Status is required"

        if not self.workspace_field.value:
            return False, "Workspace is required"

        if not self.role_field.value:
            return False, "Role is required"

        if not self.contract_type_field.value:
            return False, "Contract type is required"

        if not self.entry_date_field.value.strip():
            return False, "Entry date is required"

        # Validate date format
        try:
            day, month, year = map(int, self.entry_date_field.value.split('/'))
            date(year, month, day)
        except ValueError:
            return False, "Invalid date format. Use DD/MM/YYYY"

        return True, None

    def _parse_date(self, date_string: str) -> date:
        """Parse date from DD/MM/YYYY format."""
        day, month, year = map(int, date_string.split('/'))
        return date(year, month, day)

    def _save_employee(self):
        """Save employee (create or update)."""
        # Validate form
        is_valid, error_msg = self._validate_form()

        if not is_valid:
            self._show_error(error_msg)
            return

        try:
            from employee.models import Employee

            # Parse form data
            entry_date = self._parse_date(self.entry_date_field.value)

            if self.is_edit_mode:
                # Update existing employee
                emp = self.controller.get_employee_by_id(self.employee_id)
                if not emp:
                    self._show_error("Employee not found")
                    return

                # Update fields
                emp.first_name = self.first_name_field.value.strip()
                emp.last_name = self.last_name_field.value.strip()
                emp.external_id = self.external_id_field.value.strip() or None
                emp.current_status = self.status_field.value
                emp.workspace = self.workspace_field.value
                emp.role = self.role_field.value
                emp.contract_type = self.contract_type_field.value
                emp.entry_date = entry_date

                emp.save()
                self._show_success("Employee updated successfully")
            else:
                # Create new employee
                Employee.create(
                    first_name=self.first_name_field.value.strip(),
                    last_name=self.last_name_field.value.strip(),
                    external_id=self.external_id_field.value.strip() or None,
                    current_status=self.status_field.value,
                    workspace=self.workspace_field.value,
                    role=self.role_field.value,
                    contract_type=self.contract_type_field.value,
                    entry_date=entry_date,
                )
                self._show_success("Employee created successfully")

            # Navigate back to employees list
            self._navigate_to_employees_list()

        except Exception as e:
            self._show_error(f"Error saving employee: {str(e)}")

    def _show_error(self, message: str):
        """Show error message."""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"❌ {message}"),
                bgcolor=ft.Colors.RED,
            )
        )

    def _show_success(self, message: str):
        """Show success message."""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"✅ {message}"),
                bgcolor=ft.Colors.GREEN,
            )
        )

    def _navigate_back(self):
        """Navigate back to employees list."""
        self._navigate_to_employees_list()

    def _navigate_to_employees_list(self):
        """Navigate to employees list view."""
        self.page.clean()
        from ui.views.employees import EmployeesListView
        employees_view = EmployeesListView(self.page)
        self.page.add(
            ft.AppBar(title=ft.Text("Employee Manager")),
            employees_view.build(),
        )
        self.page.update()
