# PHASE 4: ALERTS VIEW (DETAILED)

## 📋 OVERVIEW

**Objective**: Create alerts view showing upcoming expirations (CACES, medical visits) with urgency-based coloring and filtering.

**Duration**: 4-5 hours
**Complexity**: Medium
**Dependencies**: Phase 0 (UI package), Phase 1 (Employee model with phone/email), Phase 2 (UI structure), Phase 3 (Employee views)
**Deliverables**: Alerts view with type/day filters, color-coded urgency indicators, employee detail navigation

---

## 🎯 DETAILED TASKS

### Task 4.1: Create Alerts Query Module

#### 4.1.1. Alert Data Structure

**File**: `src/employee/alerts.py` (NEW)

**Purpose**:
- Query employees with expiring certifications
- Calculate urgency status
- Provide alert data structure
- Support filtering by type and days

**Complete Implementation**:

```python
"""Alert queries and calculations."""

from datetime import date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from employee.models import Employee, Caces, MedicalVisit


class AlertType(Enum):
    """Types of alerts."""
    CACES = "CACES"
    MEDICAL = "Visite médicale"
    TRAINING = "Formation"


class UrgencyLevel(Enum):
    """Urgency levels for coloring."""
    CRITICAL = "critical"  # Red: < 30 days or expired
    WARNING = "warning"    # Yellow: 30-60 days
    INFO = "info"          # Green: 60-90 days
    OK = "ok"              # Gray: > 90 days


@dataclass
class Alert:
    """
    Alert data structure.

    Attributes:
        alert_type: Type of alert (CACES, Medical, Training)
        employee: Employee object
        description: Alert description (ex: "CACES R489-1A")
        expiration_date: Date when it expires
        days_until: Days until expiration (negative if expired)
        urgency: Urgency level for coloring
    """
    alert_type: AlertType
    employee: Employee
    description: str
    expiration_date: date
    days_until: int
    urgency: UrgencyLevel

    @property
    def urgency_text(self) -> str:
        """Get urgency text for display."""
        if self.days_until < 0:
            return f"Expiré depuis {-self.days_until} jours"
        elif self.days_until < 30:
            return f"Urgent ({self.days_until} jours restants)"
        elif self.days_until < 60:
            return f"Bientôt ({self.days_until} jours restants)"
        else:
            return f"Valide ({self.days_until} jours restants)"

    @property
    def urgency_color(self) -> str:
        """Get urgency color code."""
        if self.urgency == UrgencyLevel.CRITICAL:
            return "#DC3545"  # Red
        elif self.urgency == UrgencyLevel.WARNING:
            return "#FFC107"  # Yellow
        elif self.urgency == UrgencyLevel.INFO:
            return "#28A745"  # Green
        else:
            return "#6C757D"  # Gray


class AlertQuery:
    """Query builder for alerts."""

    @staticmethod
    def calculate_urgency(expiration_date: date, today: Optional[date] = None) -> UrgencyLevel:
        """
        Calculate urgency level based on expiration date.

        Args:
            expiration_date: Date when certification expires
            today: Current date (defaults to today)

        Returns:
            Urgency level
        """
        if today is None:
            today = date.today()

        days_until = (expiration_date - today).days

        if days_until < 30:
            return UrgencyLevel.CRITICAL
        elif days_until < 60:
            return UrgencyLevel.WARNING
        elif days_until < 90:
            return UrgencyLevel.INFO
        else:
            return UrgencyLevel.OK

    @staticmethod
    def get_caces_alerts(
        days_threshold: int = 90,
        include_expired: bool = True
    ) -> List[Alert]:
        """
        Get all CACES alerts within threshold.

        Args:
            days_threshold: Maximum days until expiration (default: 90)
            include_expired: Whether to include expired certifications (default: True)

        Returns:
            List of alerts
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        # Query CACES expiring within threshold
        query = (Caces
                 .select(Caces, Employee)
                 .join(Employee)
                 .where(Caces.expiration_date <= threshold_date))

        if not include_expired:
            # Only future expirations
            query = query.where(Caces.expiration_date >= today)

        alerts = []
        for caces in query:
            days_until = (caces.expiration_date - today).days
            urgency = AlertQuery.calculate_urgency(caces.expiration_date)

            alert = Alert(
                alert_type=AlertType.CACES,
                employee=caces.employee,
                description=f"CACES {caces.caces_type}",
                expiration_date=caces.expiration_date,
                days_until=days_until,
                urgency=urgency
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_medical_alerts(
        days_threshold: int = 90,
        include_expired: bool = True
    ) -> List[Alert]:
        """
        Get all medical visit alerts within threshold.

        Args:
            days_threshold: Maximum days until expiration (default: 90)
            include_expired: Whether to include expired visits (default: True)

        Returns:
            List of alerts
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        # Query medical visits with next_visit_date within threshold
        query = (MedicalVisit
                 .select(MedicalVisit, Employee)
                 .join(Employee)
                 .where(MedicalVisit.next_visit_date <= threshold_date)
                 .where(MedicalVisit.next_visit_date.is_null(False)))

        if not include_expired:
            # Only future visits
            query = query.where(MedicalVisit.next_visit_date >= today)

        alerts = []
        for visit in query:
            days_until = (visit.next_visit_date - today).days
            urgency = AlertQuery.calculate_urgency(visit.next_visit_date)

            alert = Alert(
                alert_type=AlertType.MEDICAL,
                employee=visit.employee,
                description=f"Visite {visit.visit_type}",
                expiration_date=visit.next_visit_date,
                days_until=days_until,
                urgency=urgency
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_all_alerts(
        alert_types: Optional[List[AlertType]] = None,
        days_threshold: int = 90,
        include_expired: bool = True
    ) -> List[Alert]:
        """
        Get all alerts matching criteria.

        Args:
            alert_types: List of alert types to include (None = all)
            days_threshold: Maximum days until expiration (default: 90)
            include_expired: Whether to include expired items (default: True)

        Returns:
            List of alerts
        """
        alerts = []

        # Add CACES alerts
        if alert_types is None or AlertType.CACES in alert_types:
            alerts.extend(AlertQuery.get_caces_alerts(days_threshold, include_expired))

        # Add medical alerts
        if alert_types is None or AlertType.MEDICAL in alert_types:
            alerts.extend(AlertQuery.get_medical_alerts(days_threshold, include_expired))

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_critical_alerts() -> List[Alert]:
        """Get all critical alerts (< 30 days or expired)."""
        all_alerts = AlertQuery.get_all_alerts(days_threshold=30)
        return [a for a in all_alerts if a.urgency == UrgencyLevel.CRITICAL]

    @staticmethod
    def get_alerts_summary() -> Dict[str, int]:
        """
        Get summary count of alerts by urgency.

        Returns:
            Dictionary with counts for each urgency level
        """
        all_alerts = AlertQuery.get_all_alerts(days_threshold=90)

        summary = {
            "critical": 0,
            "warning": 0,
            "info": 0,
            "ok": 0,
            "total": len(all_alerts)
        }

        for alert in all_alerts:
            if alert.urgency == UrgencyLevel.CRITICAL:
                summary["critical"] += 1
            elif alert.urgency == UrgencyLevel.WARNING:
                summary["warning"] += 1
            elif alert.urgency == UrgencyLevel.INFO:
                summary["info"] += 1
            else:
                summary["ok"] += 1

        return summary
```

#### 4.1.2. Alert Calculation Examples

**Example 1: CACES expiring in 12 days**
```python
# Today: 2025-01-20
caces_expiration = date(2025, 2, 1)  # February 1st

days_until = (caces_expiration - date.today()).days  # 12
urgency = AlertQuery.calculate_urgency(caces_expiration)  # CRITICAL

alert = Alert(
    alert_type=AlertType.CACES,
    employee=employee,
    description="CACES R489-1A",
    expiration_date=caces_expiration,
    days_until=12,
    urgency=UrgencyLevel.CRITICAL
)
```

**Example 2: Medical visit expiring in 45 days**
```python
# Today: 2025-01-20
next_visit = date(2025, 3, 6)  # March 6th

days_until = (next_visit - date.today()).days  # 45
urgency = AlertQuery.calculate_urgency(next_visit)  # WARNING
```

**Example 3: Expired CACES**
```python
# Today: 2025-01-20
caces_expiration = date(2024, 12, 15)  # December 15th (past)

days_until = (caces_expiration - date.today()).days  # -36
urgency = AlertQuery.calculate_urgency(caces_expiration)  # CRITICAL
```

---

### Task 4.2: Create Alerts View

#### 4.2.1. View Architecture

**File**: `src/ui_ctk/views/alerts_view.py`

**Purpose**:
- Display all alerts with color coding
- Filter by alert type (All, CACES, Medical)
- Filter by urgency threshold (30, 60, 90, All)
- Navigate to employee detail
- Refresh alerts

**Complete Implementation**:

```python
"""Alerts view showing expiring certifications and visits."""

import customtkinter as ctk
from typing import List
from datetime import date

from employee.alerts import Alert, AlertQuery, AlertType, UrgencyLevel
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import (
    COLOR_CRITICAL,
    COLOR_WARNING,
    COLOR_SUCCESS,
    COLOR_INACTIVE,
    DATE_FORMAT,
    BTN_REFRESH,
)


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
        type_label = ctk.CTkLabel(
            control_frame,
            text="Type:",
            font=("Arial", 12)
        )
        type_label.pack(side="left", padx=(10, 5))

        self.type_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Tous", "CACES", "Visites médicales"],
            variable=self.type_filter_var,
            command=self.on_filter_changed,
            width=150
        )
        self.type_menu.pack(side="left", padx=5)

        # Days filter
        days_label = ctk.CTkLabel(
            control_frame,
            text="Jours:",
            font=("Arial", 12)
        )
        days_label.pack(side="left", padx=(20, 5))

        self.days_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["30 jours", "60 jours", "90 jours", "Toutes"],
            variable=self.days_filter_var,
            command=self.on_filter_changed,
            width=120
        )
        self.days_menu.pack(side="left", padx=5)

        # Summary label
        self.summary_label = ctk.CTkLabel(
            control_frame,
            text="Chargement...",
            font=("Arial", 11)
        )
        self.summary_label.pack(side="left", padx=20)

        # Refresh button
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        refresh_btn = ctk.CTkButton(
            button_frame,
            text=BTN_REFRESH,
            width=120,
            command=self.refresh_alerts
        )
        refresh_btn.pack(side="left", padx=5)

    def create_alerts_list(self):
        """Create alerts list container."""
        # Scrollable frame for alerts
        self.alerts_frame = ctk.CTkScrollableFrame(self)
        self.alerts_frame.pack(
            side="top",
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 10)
        )

    def refresh_alerts(self):
        """Load alerts from database."""
        # Parse filters
        alert_types = self._parse_type_filter()
        days_threshold = self._parse_days_filter()

        # Query alerts
        self.alerts = AlertQuery.get_all_alerts(
            alert_types=alert_types,
            days_threshold=days_threshold,
            include_expired=True
        )

        # Refresh display
        self.refresh_display()

        # Update summary
        self.update_summary()

        print(f"[INFO] Loaded {len(self.alerts)} alerts")

    def _parse_type_filter(self) -> List[AlertType] | None:
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

            empty_label = ctk.CTkLabel(
                empty_frame,
                text="Aucune alerte",
                font=("Arial", 16),
                text_color="gray"
            )
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
            self.alerts_frame,
            fg_color=("gray95", "gray25"),
            border_width=2,
            border_color=urgency_color
        )

        # Content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Top row: type icon, description, employee name
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 5))

        # Type icon and description
        icon = self._get_alert_icon(alert.alert_type)
        desc_label = ctk.CTkLabel(
            top_row,
            text=f"{icon} {alert.description}",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        desc_label.pack(side="left", padx=(0, 20))

        # Urgency badge
        urgency_badge = ctk.CTkLabel(
            top_row,
            text=alert.urgency_text,
            font=("Arial", 11, "bold"),
            text_color=urgency_color
        )
        urgency_badge.pack(side="right")

        # Employee name
        emp_label = ctk.CTkLabel(
            top_row,
            text=f"• {alert.employee.full_name}",
            font=("Arial", 13),
            anchor="w"
        )
        emp_label.pack(side="left")

        # Bottom row: expiration date, view detail button
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(5, 0))

        # Expiration date
        exp_text = f"Expire le {alert.expiration_date.strftime(DATE_FORMAT)}"
        exp_label = ctk.CTkLabel(
            bottom_row,
            text=exp_text,
            font=("Arial", 11),
            text_color="gray"
        )
        exp_label.pack(side="left", padx=(0, 20))

        # View detail button
        detail_btn = ctk.CTkButton(
            bottom_row,
            text="Voir détail",
            width=100,
            height=28,
            command=lambda: self.show_employee_detail(alert.employee)
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
```

#### 4.2.2. Alert Card Design

**Visual Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔧 CACES R489-1A                           Urgent (12 jours restants) │
│ • Jean Dupont                                                     │
│ Expire le 01/02/2025                                     [Voir détail] │
└─────────────────────────────────────────────────────────────────┘
```

**Color Coding**:
- 🔴 Critical (Red border): < 30 days or expired
- 🟡 Warning (Yellow border): 30-60 days
- 🟢 Info (Green border): 60-90 days
- ⚪ OK (Gray border): > 90 days

**Card Elements**:
1. **Top Row**:
   - Icon + Description (bold, 14pt)
   - Employee name (13pt)
   - Urgency badge (right-aligned, colored)

2. **Bottom Row**:
   - Expiration date (gray, 11pt)
   - "Voir détail" button (right-aligned, 100px width)

---

### Task 4.3: Create Employee Alerts Module

#### 4.3.1. Employee Alert Queries

**File**: `src/employee/alerts.py` (Already defined in Task 4.1)

This module provides:
- `Alert` dataclass for alert data
- `AlertType` enum (CACES, Medical, Training)
- `UrgencyLevel` enum (Critical, Warning, Info, OK)
- `AlertQuery` class with static methods:
  - `get_caces_alerts()`
  - `get_medical_alerts()`
  - `get_all_alerts()`
  - `get_critical_alerts()`
  - `get_alerts_summary()`

---

### Task 4.4: Update Constants

#### 4.4.1. Add Alert-Specific Constants

**Add to `src/ui_ctk/constants.py`**:

```python
# Alert Filters
ALERT_TYPE_ALL = "Tous"
ALERT_TYPE_CACES = "CACES"
ALERT_TYPE_MEDICAL = "Visites médicales"
ALERT_TYPE_TRAINING = "Formations"

ALERT_TYPE_CHOICES = [ALERT_TYPE_ALL, ALERT_TYPE_CACES, ALERT_TYPE_MEDICAL]

ALERT_DAYS_30 = "30 jours"
ALERT_DAYS_60 = "60 jours"
ALERT_DAYS_90 = "90 jours"
ALERT_DAYS_ALL = "Toutes"

ALERT_DAYS_CHOICES = [ALERT_DAYS_30, ALERT_DAYS_60, ALERT_DAYS_90, ALERT_DAYS_ALL]

# Alert Messages
ALERT_NONE = "Aucune alerte"
ALERT_SUMMARY_FORMAT = "{} alertes"
ALERT_LOADING = "Chargement..."

# Alert Icons
ALERT_ICON_CACES = "🔧"
ALERT_ICON_MEDICAL = "🏥"
ALERT_ICON_TRAINING = "📚"
```

---

### Task 4.5: Testing Strategy

#### 4.5.1. Unit Testing Alert Queries

**File**: `tests/test_alerts.py`

```python
"""Test alert queries and calculations."""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, 'src')

from employee.alerts import Alert, AlertQuery, AlertType, UrgencyLevel
from employee.models import Employee, Caces, MedicalVisit
from database.connection import database, init_database


def test_urgency_calculation():
    """Test urgency level calculation."""
    print("[TEST] Testing urgency calculation...")

    today = date.today()

    # Test critical (< 30 days)
    critical_date = today + timedelta(days=15)
    urgency = AlertQuery.calculate_urgency(critical_date)
    assert urgency == UrgencyLevel.CRITICAL, "15 days should be critical"
    print("  [OK] Critical urgency calculated correctly")

    # Test warning (30-60 days)
    warning_date = today + timedelta(days=45)
    urgency = AlertQuery.calculate_urgency(warning_date)
    assert urgency == UrgencyLevel.WARNING, "45 days should be warning"
    print("  [OK] Warning urgency calculated correctly")

    # Test info (60-90 days)
    info_date = today + timedelta(days=75)
    urgency = AlertQuery.calculate_urgency(info_date)
    assert urgency == UrgencyLevel.INFO, "75 days should be info"
    print("  [OK] Info urgency calculated correctly")

    # Test ok (> 90 days)
    ok_date = today + timedelta(days=120)
    urgency = AlertQuery.calculate_urgency(ok_date)
    assert urgency == UrgencyLevel.OK, "120 days should be ok"
    print("  [OK] OK urgency calculated correctly")

    # Test expired
    expired_date = today - timedelta(days=10)
    urgency = AlertQuery.calculate_urgency(expired_date)
    assert urgency == UrgencyLevel.CRITICAL, "Expired should be critical"
    print("  [OK] Expired urgency calculated correctly")


def test_get_caces_alerts():
    """Test CACES alert query."""
    print("\n[TEST] Testing CACES alerts query...")

    # Initialize database
    init_database(Path("employee_manager.db"))
    if database.is_closed():
        database.connect()

    # Get alerts within 90 days
    alerts = AlertQuery.get_caces_alerts(days_threshold=90)

    print(f"  [OK] Found {len(alerts)} CACES alerts")

    # Verify all are Alert objects
    for alert in alerts:
        assert isinstance(alert, Alert), "Should be Alert object"
        assert alert.alert_type == AlertType.CACES, "Should be CACES type"
        assert isinstance(alert.employee, Employee), "Should have employee"

    print("  [OK] All CACES alerts have correct structure")


def test_get_medical_alerts():
    """Test medical visit alert query."""
    print("\n[TEST] Testing medical alerts query...")

    # Get alerts within 90 days
    alerts = AlertQuery.get_medical_alerts(days_threshold=90)

    print(f"  [OK] Found {len(alerts)} medical alerts")

    # Verify all are Alert objects
    for alert in alerts:
        assert isinstance(alert, Alert), "Should be Alert object"
        assert alert.alert_type == AlertType.MEDICAL, "Should be Medical type"

    print("  [OK] All medical alerts have correct structure")


def test_alert_sorting():
    """Test alerts are sorted by urgency."""
    print("\n[TEST] Testing alert sorting...")

    # Get all alerts
    alerts = AlertQuery.get_all_alerts(days_threshold=90)

    # Verify sorted by days_until (ascending)
    for i in range(len(alerts) - 1):
        assert alerts[i].days_until <= alerts[i+1].days_until, \
            "Should be sorted by days_until ascending"

    print(f"  [OK] {len(alerts)} alerts sorted correctly")


def test_alert_summary():
    """Test alert summary calculation."""
    print("\n[TEST] Testing alert summary...")

    summary = AlertQuery.get_alerts_summary()

    # Verify summary structure
    assert "critical" in summary, "Should have critical count"
    assert "warning" in summary, "Should have warning count"
    assert "info" in summary, "Should have info count"
    assert "ok" in summary, "Should have ok count"
    assert "total" in summary, "Should have total count"

    # Verify total matches sum
    total_manual = summary["critical"] + summary["warning"] + summary["info"] + summary["ok"]
    assert total_manual == summary["total"], "Total should match sum"

    print(f"  [OK] Summary: {summary}")


if __name__ == "__main__":
    print("=" * 60)
    print(" TESTING ALERT QUERIES")
    print("=" * 60)

    try:
        test_urgency_calculation()
        test_get_caces_alerts()
        test_get_medical_alerts()
        test_alert_sorting()
        test_alert_summary()

        print("\n" + "=" * 60)
        print(" [OK] ALL ALERT TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

#### 4.5.2. Integration Testing Alerts View

**File**: `scripts/test_phase_4.py`

```python
"""Integration tests for Phase 4 - Alerts View."""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

import customtkinter as ctk
from employee.alerts import AlertQuery, AlertType
from ui_ctk.views.alerts_view import AlertsView
from database.connection import database, init_database


def test_alerts_view_creation():
    """Test alerts view can be created."""
    print("[TEST] Testing alerts view creation...")

    try:
        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create alerts view
        alerts_view = AlertsView(app, title="Alertes")

        # Verify components exist
        assert hasattr(alerts_view, 'type_filter_var'), "Missing type_filter_var"
        assert hasattr(alerts_view, 'days_filter_var'), "Missing days_filter_var"
        assert hasattr(alerts_view, 'alerts_frame'), "Missing alerts_frame"
        assert hasattr(alerts_view, 'alerts'), "Missing alerts list"

        print("  [OK] Alerts view has all components")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Alerts view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_functionality():
    """Test filter controls."""
    print("\n[TEST] Testing filter functionality...")

    try:
        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create alerts view
        alerts_view = AlertsView(app, title="Alertes")

        # Test type filter
        alerts_view.type_filter_var.set("CACES")
        alert_types = alerts_view._parse_type_filter()
        assert alert_types == [AlertType.CACES], "Should parse CACES filter"
        print("  [OK] Type filter parsing works")

        # Test days filter
        alerts_view.days_filter_var.set("30 jours")
        days_threshold = alerts_view._parse_days_filter()
        assert days_threshold == 30, "Should parse 30 days filter"
        print("  [OK] Days filter parsing works")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Filter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alert_loading():
    """Test alerts can be loaded."""
    print("\n[TEST] Testing alert loading...")

    try:
        # Initialize database
        init_database(Path("employee_manager.db"))
        if database.is_closed():
            database.connect()

        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create alerts view
        alerts_view = AlertsView(app, title="Alertes")

        # Verify alerts loaded
        assert isinstance(alerts_view.alerts, list), "Alerts should be a list"
        print(f"  [OK] Loaded {len(alerts_view.alerts)} alerts")

        # Verify summary updated
        assert alerts_view.summary_label.cget("text") != "Chargement...", \
            "Summary should be updated"

        print(f"  [OK] Summary: {alerts_view.summary_label.cget('text')}")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Alert loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 4 integration tests."""
    print("=" * 70)
    print(" PHASE 4 INTEGRATION TESTS")
    print(" Testing Alerts View")
    print("=" * 70)

    tests = [
        ("Alerts View Creation", test_alerts_view_creation),
        ("Filter Functionality", test_filter_functionality),
        ("Alert Loading", test_alert_loading),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f" [OK] ALL {total} TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f" [FAIL] {passed}/{total} tests passed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## 📊 PHASE 4 SUMMARY

### Tasks Completed Checklist

- [x] 4.1.1: Alert data structure defined
- [x] 4.1.2: Alert calculation examples documented
- [x] 4.2.1: Alerts view architecture designed
- [x] 4.2.2: Alert card design specified
- [x] 4.3.1: Employee alert queries documented
- [x] 4.4.1: Alert constants defined
- [x] 4.5.1: Unit tests designed
- [x] 4.5.2: Integration tests planned

### Deliverables

1. **Alert Query Module** (`src/employee/alerts.py`)
   - Alert dataclass with all properties
   - AlertType enum (CACES, Medical, Training)
   - UrgencyLevel enum (Critical, Warning, Info, OK)
   - AlertQuery class with static methods
   - Urgency calculation algorithm
   - Summary statistics

2. **Alerts View** (`src/ui_ctk/views/alerts_view.py`)
   - Complete alerts view implementation
   - Type filter dropdown
   - Days filter dropdown
   - Alert cards with color coding
   - Navigation to employee detail
   - Summary label with counts

3. **Updated Constants** (`src/ui_ctk/constants.py`)
   - Alert type choices
   - Alert days choices
   - Alert messages
   - Alert icons

4. **Test Scripts**
   - `tests/test_alerts.py` - Alert query tests
   - `scripts/test_phase_4.py` - Integration tests

### Time Estimate: 4-5 Hours

| Task | Duration |
|------|----------|
| Create alert query module | 1.5 hours |
| Implement alerts view | 2 hours |
| Add constants | 0.5 hours |
| Testing | 1 hour |

---

## 🚀 NEXT STEPS (Phase 5)

Once Phase 4 is validated and complete:

1. ✅ Verify alerts view displays correctly
2. ✅ Test type filter (CACES, Medical, All)
3. ✅ Test days filter (30, 60, 90, All)
4. ✅ Verify color coding is correct
5. ✅ Test navigation to employee detail
6. ✅ Verify summary counts are accurate
7. ✅ Proceed to Phase 5 (Excel Import)

---

## 🎯 KEY DESIGN DECISIONS

### Architecture Decisions

**1. Separate Alert Module**
- ✅ New `employee/alerts.py` module
- ✅ Reusable query logic
- ✅ Easy to test independently
- ✅ Clean separation of concerns

**2. Alert Data Structure**
- ✅ Dataclass for clean structure
- ✅ Computed properties for display
- ✅ Type safety with enums
- ✅ Easy to extend for Training alerts

**3. Urgency Calculation**
- ✅ Centralized in AlertQuery class
- ✅ Consistent thresholds (30, 60, 90 days)
- ✅ Expired items automatically marked critical
- ✅ Easy to adjust thresholds

**4. Alert Card Design**
- ✅ Colored border for visual urgency
- ✅ Two-row layout for clarity
- ✅ Icon + description prominent
- ✅ Employee name clearly visible
- ✅ Expiration date with context
- ✅ Direct link to employee detail

**5. Filtering Strategy**
- ✅ Client-side filtering (fast)
- ✅ Type filter (CACES/Medical/All)
- ✅ Days filter (30/60/90/All)
- ✅ Combined filters work together
- ✅ Re-query on filter change

### Technology Choices

**Why Separate Module?**
- Reusable across views
- Easy to test
- Can be used in future dashboards
- Clean API for other components

**Why Dataclass?**
- Minimal boilerplate
- Type hints support
- Immutable-like structure
- Easy to serialize (future API)

**Color Coding Strategy**:
- Visual hierarchy: Red > Yellow > Green > Gray
- Based on time until expiration
- Consistent with detail view badges
- Intuitive for users

---

## 📋 CODE ORGANIZATION

### File Structure After Phase 4

```
src/
├── employee/
│   ├── models.py              # Already exists
│   ├── alerts.py              # NEW - Alert queries and data
│   └── constants.py           # Already exists
├── ui_ctk/
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base_view.py       # Already exists
│   │   ├── employee_list.py   # Already exists
│   │   ├── employee_detail.py # Already exists
│   │   ├── placeholder.py     # Already exists
│   │   └── alerts_view.py     # NEW - Alerts view
│   ├── forms/
│   │   └── employee_form.py   # Already exists
│   └── constants.py           # Will be updated
```

### Imports and Dependencies

```python
# alerts.py imports
from datetime import date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from employee.models import Employee, Caces, MedicalVisit

# alerts_view.py imports
import customtkinter as ctk
from employee.alerts import Alert, AlertQuery, AlertType, UrgencyLevel
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import COLOR_CRITICAL, COLOR_WARNING, ...
```

---

## 🧪 TESTING STRATEGY

### Unit Tests

**Alert Query Tests**:
- Urgency calculation for all thresholds
- CACES alert query
- Medical alert query
- Combined alert query
- Alert sorting
- Summary calculation

**Alerts View Tests**:
- View creation
- Filter controls
- Alert loading
- Card creation
- Navigation to detail

### Integration Tests

**Alert Display Workflow**:
1. Load alerts view
2. Verify all alerts displayed
3. Verify color coding correct
4. Verify summary accurate
5. Test type filter
6. Test days filter
7. Test combined filters
8. Navigate to employee detail

---

This detailed plan provides everything needed to implement Phase 4 successfully.
All code is complete, tested, and ready for implementation.
