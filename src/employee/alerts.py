"""Alert queries and calculations."""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional

from employee.models import Caces, Employee, MedicalVisit


class AlertType(Enum):
    """Types of alerts."""

    CACES = "CACES"
    MEDICAL = "Visite médicale"
    TRAINING = "Formation"


class UrgencyLevel(Enum):
    """Urgency levels for coloring."""

    CRITICAL = "critical"  # Red: < 30 days or expired
    WARNING = "warning"  # Yellow: 30-60 days
    INFO = "info"  # Green: 60-90 days
    OK = "ok"  # Gray: > 90 days


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
    def get_caces_alerts(days_threshold: int = 90, include_expired: bool = True) -> List[Alert]:
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
        query = Caces.select(Caces, Employee).join(Employee).where(Caces.expiration_date <= threshold_date)

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
                description=f"CACES {caces.kind}",
                expiration_date=caces.expiration_date,
                days_until=days_until,
                urgency=urgency,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_medical_alerts(days_threshold: int = 90, include_expired: bool = True) -> List[Alert]:
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

        # Query medical visits with expiration_date within threshold
        query = (
            MedicalVisit.select(MedicalVisit, Employee)
            .join(Employee)
            .where(MedicalVisit.expiration_date <= threshold_date)
        )

        if not include_expired:
            # Only future expirations
            query = query.where(MedicalVisit.expiration_date >= today)

        alerts = []
        for visit in query:
            days_until = (visit.expiration_date - today).days
            urgency = AlertQuery.calculate_urgency(visit.expiration_date)

            alert = Alert(
                alert_type=AlertType.MEDICAL,
                employee=visit.employee,
                description=f"Visite {visit.visit_type}",
                expiration_date=visit.expiration_date,
                days_until=days_until,
                urgency=urgency,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_all_alerts(
        alert_types: Optional[List[AlertType]] = None, days_threshold: int = 90, include_expired: bool = True
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

        summary = {"critical": 0, "warning": 0, "info": 0, "ok": 0, "total": len(all_alerts)}

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
