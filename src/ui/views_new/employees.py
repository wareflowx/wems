"""Employees list view - Displays list of all employees with filtering.

Updated to use new professional components and router navigation.
"""

import flet as ft
from typing import List

from ui.controllers.employee_controller import EmployeeController
from ui.components.inputs import SearchField, AppDropdown
from ui.components.chips import FilterChipGroup, StatusBadge
from ui.components.icons import Icons
from ui.components.cards import AppCard
from ui.constants import Spacing
from ui.navigation.router import get_router
from ui.theme_colors import get_theme_colors, get_success_color, get_warning_color, get_error_color


class EmployeesListView:
    """
    Employees list view builder using professional components.

    Constructs a searchable, filterable list of employees
    with navigation to detail views.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize employees list view.

        Args:
            page: The Flet page instance
        """
        self.page = page
        self.controller = EmployeeController()

        # Filter state
        self.search_text = ""
        self.filter_status = "all"  # all, active, inactive
        self.employees_data = []
        self._colors = get_theme_colors(page)

    def build(self) -> ft.Column:
        """
        Build the employees list view.

        Returns:
            ft.Column containing search, filters, and employee list
        """
        # Load employees
        self.employees_data = self._load_employees()

        # Build components
        search_row = self._build_search_row()
        filters_row = self._build_filters_row()
        employees_list = self._build_employees_list()

        # Assemble view content
        view_content = ft.Column(
            [
                ft.Container(height=Spacing.LG.value),
                ft.Text(
                    "Employees",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=Spacing.MD.value),
                search_row,
                ft.Container(height=Spacing.SM.value),
                filters_row,
                ft.Container(height=Spacing.LG.value),
                employees_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return view_content

    def _load_employees(self) -> List[dict]:
        """
        Load employees with their compliance scores.

        Returns:
            List of employee dictionaries with display data
        """
        from employee import calculations

        employees = self.controller.get_all_employees()
        employees_data = []

        for emp in employees:
            score_data = calculations.calculate_compliance_score(emp)
            employees_data.append({
                'id': str(emp.id),
                'name': emp.full_name,
                'status': emp.current_status,
                'workspace': emp.workspace,
                'role': emp.role,
                'compliance_score': score_data['score'],
            })

        return employees_data

    def _build_search_row(self) -> ft.Container:
        """Build search input row."""
        search_field = SearchField(
            placeholder="Search employees by name...",
            on_change=self._on_search_change,
            width=600,
        )

        return ft.Container(
            content=search_field,
            width=600,
        )

    def _build_filters_row(self) -> ft.Row:
        """Build filter buttons row."""
        filter_chips = FilterChipGroup(
            options=[
                ("all", "All"),
                ("active", "Active"),
                ("inactive", "Inactive"),
            ],
            selected=self.filter_status,
            on_change=self._on_filter_change,
        )

        return ft.Row(
            [
                ft.Text(
                    "Filter:",
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(width=Spacing.SM.value),
                filter_chips,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _build_employees_list(self) -> AppCard:
        """Build the employees list."""
        # Filter employees based on current filters
        filtered_employees = self._filter_employees()

        # Build list items
        list_items = []

        if not filtered_employees:
            # No employees message
            list_items.append(
                ft.Column(
                    [
                        ft.Icon(
                            Icons.SEARCH,
                            size=48,
                            color=self._colors["on_surface_variant"],
                        ),
                        ft.Container(height=Spacing.SM.value),
                        ft.Text(
                            "No employees found",
                            size=16,
                            color=self._colors["on_surface"],
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "Try adjusting your filters or search",
                            size=12,
                            color=self._colors["on_surface_variant"],
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        else:
            # Create employee list items
            for emp_data in filtered_employees:
                list_items.append(
                    self._build_employee_item(emp_data)
                )

        count_text = f"{len(filtered_employees)} employee{'s' if len(filtered_employees) != 1 else ''}"

        content = ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Text(
                            "All Employees",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            count_text,
                            size=13,
                            color=self._colors["on_surface_variant"],
                        ),
                    ],
                ),
                ft.Divider(height=1),
                # Employee list
                ft.Column(
                    list_items,
                    spacing=Spacing.XS.value,
                ),
            ],
            spacing=Spacing.SM.value,
        )

        return AppCard(content=content)

    def _build_employee_item(self, emp_data: dict) -> ft.Container:
        """Build a single employee list item."""
        # Determine styling based on compliance
        if emp_data['compliance_score'] >= 70:
            compliance_color = get_success_color()
            compliance_text = "Compliant"
        elif emp_data['compliance_score'] >= 50:
            compliance_color = get_warning_color()
            compliance_text = "Warning"
        else:
            compliance_color = get_error_color()
            compliance_text = "Critical"

        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(Icons.PERSON, size=32),
                title=ft.Text(
                    emp_data['name'],
                    size=15,
                    weight=ft.FontWeight.W_500,
                ),
                subtitle=ft.Column(
                    [
                        ft.Text(
                            f"{emp_data['workspace']} • {emp_data['role']}",
                            size=12,
                            color=self._colors["on_surface_variant"],
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            [
                                StatusBadge(
                                    status=emp_data['status'],
                                    variant="active" if emp_data['status'] == 'active' else "inactive",
                                    size="sm",
                                ),
                                ft.Container(width=Spacing.SM.value),
                                ft.Text(
                                    f"{emp_data['compliance_score']}%",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=compliance_color,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=0,
                ),
                trailing=ft.Icon(
                    Icons.CHEVRON_RIGHT,
                    size=20,
                    color=self._colors["on_surface_variant"],
                ),
            ),
            bgcolor=self._colors["surface_variant"] if emp_data['status'] == 'inactive' else None,
            border_radius=8,
            on_click=lambda e: self._navigate_to_employee(emp_data['id']),
            ink=True,
        )

    def _filter_employees(self) -> List[dict]:
        """
        Filter employees based on search and status filters.

        Returns:
            Filtered list of employee dictionaries
        """
        filtered = self.employees_data

        # Apply status filter
        if self.filter_status != "all":
            filtered = [e for e in filtered if e['status'] == self.filter_status]

        # Apply search filter
        if self.search_text:
            search_lower = self.search_text.lower()
            filtered = [
                e for e in filtered
                if search_lower in e['name'].lower()
            ]

        return filtered

    def _on_search_change(self, e):
        """Handle search text change."""
        self.search_text = e.control.value
        self._refresh_list()

    def _on_filter_change(self, value: str):
        """Handle filter chip change."""
        self.filter_status = value
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the employees list display."""
        router = get_router(self.page)
        router.replace(self.page.route)

    def _navigate_to_employee(self, employee_id: str):
        """Navigate to employee detail view."""
        router = get_router(self.page)
        router.navigate("/employee", id=employee_id)
