"""Alerts view showing expiring certifications and visits."""

from typing import List

import customtkinter as ctk

from employee.alerts import Alert, AlertQuery, AlertType, UrgencyLevel
from ui_ctk.constants import (
    BTN_REFRESH,
    DATE_FORMAT,
)
from ui_ctk.views.base_view import BaseView


class AlertsView(BaseView):
    """
    Alerts view with expiring certifications and medical visits.

    Features:
    - Display all alerts with color coding
    - Filter by type (All, CACES, Medical)
    - Filter by urgency threshold (30, 60, 90, All days)
    - Navigate to employee detail
    - Show urgency with badges
    """

    def __init__(self, master, title: str = "Alertes"):
        super().__init__(master, title=title)

        # State
        self.alerts: List[Alert] = []
        self.alert_widgets: List[ctk.CTkFrame] = []

        # Filter variables
        self.type_filter_var = ctk.StringVar(value="Tous")
        self.days_filter_var = ctk.StringVar(value="90 jours")

        # UI Components
        self.create_controls()
        self.create_alerts_list()

        # Load alerts
        self.refresh_alerts()

    def create_controls(self):
        """Create filter controls."""
        # Control frame
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        control_frame.pack_propagate(False)

        # Type filter
        type_label = ctk.CTkLabel(control_frame, text="Type:", font=("Arial", 12))
        type_label.pack(side="left", padx=(10, 5))

        self.type_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Tous", "CACES", "Visites médicales"],
            variable=self.type_filter_var,
            command=self.on_filter_changed,
            width=150,
        )
        self.type_menu.pack(side="left", padx=5)

        # Days filter
        days_label = ctk.CTkLabel(control_frame, text="Jours:", font=("Arial", 12))
        days_label.pack(side="left", padx=(20, 5))

        self.days_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["30 jours", "60 jours", "90 jours", "Toutes"],
            variable=self.days_filter_var,
            command=self.on_filter_changed,
            width=120,
        )
        self.days_menu.pack(side="left", padx=5)

        # Summary label
        self.summary_label = ctk.CTkLabel(control_frame, text="Chargement...", font=("Arial", 11))
        self.summary_label.pack(side="left", padx=20)

        # Refresh button
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        refresh_btn = ctk.CTkButton(button_frame, text=BTN_REFRESH, width=120, command=self.refresh_alerts)
        refresh_btn.pack(side="left", padx=5)

    def create_alerts_list(self):
        """Create alerts list container."""
        # Scrollable frame for alerts
        self.alerts_frame = ctk.CTkScrollableFrame(self)
        self.alerts_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))

    def refresh_alerts(self):
        """Load alerts from database."""
        # Parse filters
        alert_types = self._parse_type_filter()
        days_threshold = self._parse_days_filter()

        # Query alerts
        self.alerts = AlertQuery.get_all_alerts(
            alert_types=alert_types, days_threshold=days_threshold, include_expired=True
        )

        # Refresh display
        self.refresh_display()

        # Update summary
        self.update_summary()

        print(f"[INFO] Loaded {len(self.alerts)} alerts")

    def _parse_type_filter(self):
        """Parse type filter from dropdown."""
        type_value = self.type_filter_var.get()

        if type_value == "Tous":
            return None
        elif type_value == "CACES":
            return [AlertType.CACES]
        elif type_value == "Visites médicales":
            return [AlertType.MEDICAL]
        else:
            return None

    def _parse_days_filter(self) -> int:
        """Parse days threshold from dropdown."""
        days_value = self.days_filter_var.get()

        if days_value == "30 jours":
            return 30
        elif days_value == "60 jours":
            return 60
        elif days_value == "90 jours":
            return 90
        else:  # "Toutes"
            return 9999  # Effectively all

    def refresh_display(self):
        """Rebuild alert widgets."""
        # Clear existing widgets
        for widget in self.alert_widgets:
            widget.destroy()
        self.alert_widgets.clear()

        if not self.alerts:
            # Show empty message
            empty_frame = ctk.CTkFrame(self.alerts_frame)
            empty_frame.pack(fill="both", expand=True, padx=20, pady=20)

            empty_label = ctk.CTkLabel(empty_frame, text="Aucune alerte", font=("Arial", 16), text_color="gray")
            empty_label.pack()

            self.alert_widgets.append(empty_frame)
            return

        # Create alert cards
        for alert in self.alerts:
            alert_card = self.create_alert_card(alert)
            alert_card.pack(fill="x", pady=5)
            self.alert_widgets.append(alert_card)

    def create_alert_card(self, alert: Alert) -> ctk.CTkFrame:
        """
        Create a single alert card.

        Args:
            alert: Alert object

        Returns:
            Frame containing alert card
        """
        # Determine urgency color
        urgency_color = alert.urgency_color

        # Card frame with colored border
        card = ctk.CTkFrame(
            self.alerts_frame, fg_color=("gray95", "gray25"), border_width=2, border_color=urgency_color
        )

        # Content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Top row: type icon, description, employee name
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 5))

        # Type icon and description
        icon = self._get_alert_icon(alert.alert_type)
        desc_label = ctk.CTkLabel(top_row, text=f"{icon} {alert.description}", font=("Arial", 14, "bold"), anchor="w")
        desc_label.pack(side="left", padx=(0, 20))

        # Urgency badge
        urgency_badge = ctk.CTkLabel(
            top_row, text=alert.urgency_text, font=("Arial", 11, "bold"), text_color=urgency_color
        )
        urgency_badge.pack(side="right")

        # Employee name
        emp_label = ctk.CTkLabel(top_row, text=f"• {alert.employee.full_name}", font=("Arial", 13), anchor="w")
        emp_label.pack(side="left")

        # Bottom row: expiration date, view detail button
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(5, 0))

        # Expiration date
        exp_text = f"Expire le {alert.expiration_date.strftime(DATE_FORMAT)}"
        exp_label = ctk.CTkLabel(bottom_row, text=exp_text, font=("Arial", 11), text_color="gray")
        exp_label.pack(side="left", padx=(0, 20))

        # View detail button
        detail_btn = ctk.CTkButton(
            bottom_row,
            text="Voir détail",
            width=100,
            height=28,
            command=lambda: self.show_employee_detail(alert.employee),
        )
        detail_btn.pack(side="right")

        return card

    def _get_alert_icon(self, alert_type: AlertType) -> str:
        """Get icon for alert type."""
        if alert_type == AlertType.CACES:
            return "🔧"
        elif alert_type == AlertType.MEDICAL:
            return "🏥"
        else:
            return "📚"

    def update_summary(self):
        """Update summary label."""
        if not self.alerts:
            self.summary_label.configure(text="0 alertes")
            return

        # Count by urgency
        critical = sum(1 for a in self.alerts if a.urgency == UrgencyLevel.CRITICAL)
        warning = sum(1 for a in self.alerts if a.urgency == UrgencyLevel.WARNING)
        info = sum(1 for a in self.alerts if a.urgency == UrgencyLevel.INFO)
        ok_count = sum(1 for a in self.alerts if a.urgency == UrgencyLevel.OK)

        # Build summary text
        summary_parts = []
        if critical > 0:
            summary_parts.append(f"{critical} critiques")
        if warning > 0:
            summary_parts.append(f"{warning} avertissements")
        if info > 0:
            summary_parts.append(f"{info} informations")

        if summary_parts:
            summary_text = f"{len(self.alerts)} alertes ({', '.join(summary_parts)})"
        else:
            summary_text = f"{len(self.alerts)} alertes"

        self.summary_label.configure(text=summary_text)

    def on_filter_changed(self, value):
        """Handle filter change."""
        self.refresh_alerts()

    def show_employee_detail(self, employee):
        """Navigate to employee detail view."""
        try:
            from ui_ctk.views.employee_detail import EmployeeDetailView

            main_window = self.master_window
            main_window.switch_view(EmployeeDetailView, employee=employee)

            print(f"[NAV] Showing detail for {employee.full_name}")

        except Exception as e:
            print(f"[ERROR] Failed to show employee detail: {e}")

    def refresh(self):
        """Refresh the view (called by parent)."""
        self.refresh_alerts()
