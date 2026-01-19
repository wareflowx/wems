"""Employees list view - Displays list of all employees with filtering."""

import flet as ft
from typing import List, Optional

from ui.controllers.employee_controller import EmployeeController
from ui.widgets.employee_list_item import EmployeeListItem


class EmployeesListView:
    """
    Employees list view builder.

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
        self.filter_chips = {}  # Will be populated in _build_filters_row

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

        # Assemble view
        return ft.Column(
            [
                search_row,
                ft.Container(height=10),
                filters_row,
                ft.Container(height=20),
                employees_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

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

    def _build_search_row(self) -> ft.Row:
        """Build search input row."""
        search_field = ft.TextField(
            hint_text="🔍 Search employees by name...",
            width=600,
            autofocus=False,
            on_change=self._on_search_change,
        )

        return ft.Row(
            [
                search_field,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _build_filters_row(self) -> ft.Row:
        """Build filter buttons row."""
        # Use Chip (toggle buttons) for filtering
        filter_chip_all = ft.Chip(
            label=ft.Text("All", size=12),
            selected=True,
            on_click=lambda e: self._on_filter_click(e, "all"),
        )
        filter_chip_active = ft.Chip(
            label=ft.Text("Active", size=12),
            on_click=lambda e: self._on_filter_click(e, "active"),
        )
        filter_chip_inactive = ft.Chip(
            label=ft.Text("Inactive", size=12),
            on_click=lambda e: self._on_filter_click(e, "inactive"),
        )

        # Store chip references
        self.filter_chips = {
            "all": filter_chip_all,
            "active": filter_chip_active,
            "inactive": filter_chip_inactive,
        }

        return ft.Row(
            [
                ft.Text("Filter:", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(width=10),
                ft.Row(
                    [filter_chip_all, filter_chip_active, filter_chip_inactive],
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _build_employees_list(self) -> ft.Column:
        """Build the employees list."""
        # Filter employees based on current filters
        filtered_employees = self._filter_employees()

        # Build list items
        list_items = []

        if not filtered_employees:
            # No employees message
            list_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "🔍",
                                size=48,
                            ),
                            ft.Text(
                                "No employees found",
                                size=16,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "Try adjusting your filters or search",
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30,
                )
            )
        else:
            # Create employee list items
            for emp_data in filtered_employees:
                # Create click handler for navigation
                def navigate_to_employee(e, emp_id=emp_data['id']):
                    self._navigate_to_employee_detail(emp_id)

                list_items.append(
                    EmployeeListItem(
                        employee_id=emp_data['id'],
                        employee_name=emp_data['name'],
                        status=emp_data['status'],
                        workspace=emp_data['workspace'],
                        role=emp_data['role'],
                        compliance_score=emp_data['compliance_score'],
                        on_click=navigate_to_employee,
                    )
                )

        # Count badge
        count_text = f"{len(filtered_employees)} employee{'s' if len(filtered_employees) != 1 else ''}"

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Employees",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"({count_text})",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    list_items,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=10,
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

    def _on_filter_click(self, e, filter_value: str):
        """Handle filter chip click."""
        # Update selected state
        self.filter_status = filter_value

        # Update chip visuals
        for key, chip in self.filter_chips.items():
            chip.selected = (key == filter_value)

        # Refresh list
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the employees list display."""
        self.page.clean()
        self.page.add(
            ft.AppBar(
                title=ft.Text("Employee Manager"),
                bgcolor=ft.Colors.SURFACE,
            ),
            self.build(),
        )
        self.page.update()

    def _navigate_to_employee_detail(self, employee_id: str):
        """Navigate to employee detail view."""
        self.page.clean()
        from ui.views.employee_detail import EmployeeDetailView
        detail_view = EmployeeDetailView(self.page, employee_id)
        self.page.add(
            ft.AppBar(title=ft.Text("Employee Manager")),
            detail_view.build(),
        )
        self.page.update()
