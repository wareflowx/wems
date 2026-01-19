"""Alerts view - Complete list of all alerts with filtering."""

import flet as ft
from typing import List

from ui.controllers.alerts_controller import AlertsController
from ui.widgets.alert_item import AlertListItem
from ui.widgets.navigation import NavigationBar


class AlertsView:
    """
    Alerts view builder.

    Constructs a complete, filterable list of all alerts
    with export functionality and navigation to employee details.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize alerts view.

        Args:
            page: The Flet page instance
        """
        self.page = page
        self.controller = AlertsController()

        # Filter state
        self.filter_type = "all"  # all, caces, medical, training
        self.filter_urgency = "all"  # all, urgent, high, normal
        self.alerts_data = []

    def build(self) -> ft.Column:
        """
        Build the alerts view.

        Returns:
            ft.Column containing filters and alerts list
        """
        # Load alerts
        self.alerts_data = self.controller.get_all_alerts(days=90)

        # Build components
        nav_bar = NavigationBar(self.page, current_view="alerts")
        filters_row = self._build_filters_row()
        summary_row = self._build_summary_row()
        alerts_list = self._build_alerts_list()

        # Assemble view content
        view_content = ft.Column(
            [
                ft.Container(height=20),
                filters_row,
                ft.Container(height=20),
                summary_row,
                ft.Container(height=20),
                alerts_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Column(
            [
                nav_bar,
                view_content,
            ],
        )

    def _build_filters_row(self) -> ft.Row:
        """Build filter chips row."""
        # Type filter chips
        type_filter_all = ft.Chip(
            label=ft.Text("All", size=12),
            selected=True,
            on_click=lambda e: self._on_type_filter_click(e, "all"),
        )
        type_filter_caces = ft.Chip(
            label=ft.Text("CACES", size=12),
            on_click=lambda e: self._on_type_filter_click(e, "caces"),
        )
        type_filter_medical = ft.Chip(
            label=ft.Text("Medical", size=12),
            on_click=lambda e: self._on_type_filter_click(e, "medical"),
        )
        type_filter_training = ft.Chip(
            label=ft.Text("Training", size=12),
            on_click=lambda e: self._on_type_filter_click(e, "training"),
        )

        # Urgency filter chips
        urgency_filter_all = ft.Chip(
            label=ft.Text("All", size=12),
            selected=True,
            on_click=lambda e: self._on_urgency_filter_click(e, "all"),
        )
        urgency_filter_urgent = ft.Chip(
            label=ft.Text("🔴 Urgent", size=12),
            on_click=lambda e: self._on_urgency_filter_click(e, "urgent"),
        )
        urgency_filter_high = ft.Chip(
            label=ft.Text("🟠 High", size=12),
            on_click=lambda e: self._on_urgency_filter_click(e, "high"),
        )
        urgency_filter_normal = ft.Chip(
            label=ft.Text("🟢 Normal", size=12),
            on_click=lambda e: self._on_urgency_filter_click(e, "normal"),
        )

        # Store chip references
        self.type_filter_chips = {
            "all": type_filter_all,
            "caces": type_filter_caces,
            "medical": type_filter_medical,
            "training": type_filter_training,
        }

        self.urgency_filter_chips = {
            "all": urgency_filter_all,
            "urgent": urgency_filter_urgent,
            "high": urgency_filter_high,
            "normal": urgency_filter_normal,
        }

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Type:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(width=10),
                        ft.Row(
                            [type_filter_all, type_filter_caces, type_filter_medical, type_filter_training],
                            spacing=5,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text("Urgency:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(width=10),
                        ft.Row(
                            [urgency_filter_all, urgency_filter_urgent, urgency_filter_high, urgency_filter_normal],
                            spacing=5,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

    def _build_summary_row(self) -> ft.Row:
        """Build summary statistics row."""
        summary = self.controller.get_alerts_summary(days=90)

        # Build summary items
        items = []

        # Urgent alerts
        if summary['urgent'] > 0:
            items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"🔴 {summary['urgent']}", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Urgent", size=12, color=ft.Colors.GREY_700),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=100,
                    padding=10,
                    bgcolor=ft.Colors.RED_50,
                    border_radius=8,
                )
            )

        # High alerts
        if summary['high'] > 0:
            items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"🟠 {summary['high']}", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("High", size=12, color=ft.Colors.GREY_700),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=100,
                    padding=10,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=8,
                )
            )

        # Normal alerts
        if summary['normal'] > 0:
            items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"🟢 {summary['normal']}", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Normal", size=12, color=ft.Colors.GREY_700),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=100,
                    padding=10,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=8,
                )
            )

        # Total
        items.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"{summary['total']}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Total", size=12, color=ft.Colors.GREY_700),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=100,
                padding=10,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
            )
        )

        return ft.Row(items, spacing=10)

    def _build_alerts_list(self) -> ft.Column:
        """Build the alerts list."""
        # Filter alerts based on current filters
        filtered_alerts = self._filter_alerts()

        # Build list items
        list_items = []

        if not filtered_alerts:
            # No alerts message
            list_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "✅",
                                size=48,
                            ),
                            ft.Text(
                                "No alerts found",
                                size=16,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "Try adjusting your filters",
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
            # Create alert list items
            for alert in filtered_alerts:
                # Create click handler for navigation
                def navigate_to_employee(e, emp_id=alert['employee_id']):
                    self._navigate_to_employee_detail(emp_id)

                list_items.append(
                    AlertListItem(
                        employee_name=alert['employee_name'],
                        description=alert['description'],
                        days_until=alert['days_until'],
                        priority=alert['priority'],
                        on_click=navigate_to_employee,
                    )
                )

        # Count badge
        count_text = f"{len(filtered_alerts)} alert{'s' if len(filtered_alerts) != 1 else ''}"

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Alerts",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"({count_text})",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            "📥 Export",
                            on_click=lambda e: self._export_alerts(),
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

    def _filter_alerts(self) -> List[dict]:
        """
        Filter alerts based on current filters.

        Returns:
            Filtered list of alert dictionaries
        """
        filtered = self.alerts_data

        # Apply type filter
        if self.filter_type != "all":
            filtered = [a for a in filtered if a['type'] == self.filter_type]

        # Apply urgency filter
        if self.filter_urgency != "all":
            filtered = [a for a in filtered if a['priority'] == self.filter_urgency]

        return filtered

    def _on_type_filter_click(self, e, filter_value: str):
        """Handle type filter chip click."""
        self.filter_type = filter_value

        # Update chip visuals
        for key, chip in self.type_filter_chips.items():
            chip.selected = (key == filter_value)

        self._refresh_list()

    def _on_urgency_filter_click(self, e, filter_value: str):
        """Handle urgency filter chip click."""
        self.filter_urgency = filter_value

        # Update chip visuals
        for key, chip in self.urgency_filter_chips.items():
            chip.selected = (key == filter_value)

        self._refresh_list()

    def _refresh_list(self):
        """Refresh the alerts list display."""
        self.page.clean()
        self.page.add(self.build())
        self.page.update()

    def _navigate_to_employee_detail(self, employee_id: str):
        """Navigate to employee detail view."""
        self.page.clean()
        from ui.views.employee_detail import EmployeeDetailView
        detail_view = EmployeeDetailView(self.page, employee_id)
        self.page.add(detail_view.build())
        self.page.update()

    def _export_alerts(self):
        """Export alerts to Excel (placeholder for now)."""
        # TODO: Implement Excel export
        export_data = self.controller.export_alerts_to_dict(days=90)
        print(f"Exporting {len(export_data)} alerts...")
        # For now, just show a message
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Exported {len(export_data)} alerts (feature coming soon)"),
            )
        )
