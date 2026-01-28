"""Alert queries and calculations."""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional

from constants.alerts import ALERT_CRITICAL_DAYS, DEFAULT_ALERT_DAYS
from employee.alert_settings import AlertSettingsManager
from employee.models import Caces, Contract, Employee, MedicalVisit


class AlertType(Enum):
    """Types of alerts."""

    CACES = "CACES"
    MEDICAL = "Visite médicale"
    TRAINING = "Formation"
    CONTRACT = "Contrat"


class UrgencyLevel(Enum):
    """Urgency levels for coloring."""

    CRITICAL = "critical"  # Red: Most urgent
    WARNING = "warning"  # Yellow/Orange: Medium urgency
    INFO = "info"  # Green: Low urgency
    OK = "ok"  # Gray: No urgency


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
        urgency: Urgency level for coloring (deprecated, use alert_level)
        alert_level: Configurable alert level from settings
        custom_color: Custom color from settings (optional)
        custom_label: Custom label from settings (optional)
    """

    alert_type: AlertType
    employee: Employee
    description: str
    expiration_date: date
    days_until: int
    urgency: UrgencyLevel
    alert_level: Optional[str] = None  # "critical", "alert", "warning", "info"
    custom_color: Optional[str] = None
    custom_label: Optional[str] = None

    @property
    def urgency_text(self) -> str:
        """Get urgency text for display."""
        # Use custom label if available
        if self.custom_label:
            if self.days_until < 0:
                return f"{self.custom_label} - Expiré depuis {-self.days_until} jours"
            else:
                return f"{self.custom_label} ({self.days_until} jours restants)"

        # Fallback to default text
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
        # Use custom color if available
        if self.custom_color:
            return self.custom_color

        # Fallback to default colors
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

    # Class-level settings manager (shared across all instances)
    _settings_manager: Optional[AlertSettingsManager] = None

    @classmethod
    def get_settings_manager(cls) -> AlertSettingsManager:
        """Get or create the shared settings manager."""
        if cls._settings_manager is None:
            cls._settings_manager = AlertSettingsManager()
        return cls._settings_manager

    @classmethod
    def set_settings_manager(cls, settings_manager: AlertSettingsManager):
        """Set a custom settings manager (for testing)."""
        cls._settings_manager = settings_manager

    @staticmethod
    def calculate_urgency(expiration_date: date, today: Optional[date] = None, category: str = "caces") -> UrgencyLevel:
        """
        Calculate urgency level based on expiration date and configurable settings.

        Args:
            expiration_date: Date when certification expires
            today: Current date (defaults to today)
            category: Document category for configurable thresholds

        Returns:
            Urgency level
        """
        if today is None:
            today = date.today()

        days_until = (expiration_date - today).days

        # Use configurable settings to determine urgency
        settings_manager = AlertQuery.get_settings_manager()
        alert_level = settings_manager.get_alert_level(category, days_until)

        if alert_level:
            # Map alert level label to urgency
            label = alert_level.label.lower()
            if "critical" in label:
                return UrgencyLevel.CRITICAL
            elif "alert" in label:
                return UrgencyLevel.CRITICAL  # Alert level maps to critical urgency
            elif "warning" in label:
                return UrgencyLevel.WARNING
            else:  # info
                return UrgencyLevel.INFO
        else:
            # No alert level configured, return OK
            return UrgencyLevel.OK

    @staticmethod
    def get_caces_alerts(days_threshold: int = DEFAULT_ALERT_DAYS, include_expired: bool = True) -> List[Alert]:
        """
        Get all CACES alerts within threshold.

        Args:
            days_threshold: Maximum days until expiration (default: DEFAULT_ALERT_DAYS)
            include_expired: Whether to include expired certifications (default: True)

        Returns:
            List of alerts
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        settings_manager = AlertQuery.get_settings_manager()

        # Query CACES expiring within threshold
        query = Caces.select(Caces, Employee).join(Employee).where(Caces.expiration_date <= threshold_date)

        if not include_expired:
            # Only future expirations
            query = query.where(Caces.expiration_date >= today)

        alerts = []
        for caces in query:
            days_until = (caces.expiration_date - today).days
            urgency = AlertQuery.calculate_urgency(caces.expiration_date, category="caces")

            # Get configurable alert level info
            alert_level_obj = settings_manager.get_alert_level("caces", days_until)

            alert = Alert(
                alert_type=AlertType.CACES,
                employee=caces.employee,
                description=f"CACES {caces.kind}",
                expiration_date=caces.expiration_date,
                days_until=days_until,
                urgency=urgency,
                alert_level=alert_level_obj.label if alert_level_obj else None,
                custom_color=alert_level_obj.color if alert_level_obj else None,
                custom_label=alert_level_obj.label if alert_level_obj else None,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_medical_alerts(days_threshold: int = DEFAULT_ALERT_DAYS, include_expired: bool = True) -> List[Alert]:
        """
        Get all medical visit alerts within threshold.

        Args:
            days_threshold: Maximum days until expiration (default: DEFAULT_ALERT_DAYS)
            include_expired: Whether to include expired visits (default: True)

        Returns:
            List of alerts
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        settings_manager = AlertQuery.get_settings_manager()

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
            urgency = AlertQuery.calculate_urgency(visit.expiration_date, category="medical")

            # Get configurable alert level info
            alert_level_obj = settings_manager.get_alert_level("medical", days_until)

            alert = Alert(
                alert_type=AlertType.MEDICAL,
                employee=visit.employee,
                description=f"Visite {visit.visit_type}",
                expiration_date=visit.expiration_date,
                days_until=days_until,
                urgency=urgency,
                alert_level=alert_level_obj.label if alert_level_obj else None,
                custom_color=alert_level_obj.color if alert_level_obj else None,
                custom_label=alert_level_obj.label if alert_level_obj else None,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_contract_alerts(days_threshold: int = DEFAULT_ALERT_DAYS, include_expired: bool = True) -> List[Alert]:
        """
        Get all contract expiration alerts within threshold.

        Args:
            days_threshold: Maximum days until expiration (default: DEFAULT_ALERT_DAYS)
            include_expired: Whether to include expired contracts (default: True)

        Returns:
            List of alerts for contracts expiring soon
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        settings_manager = AlertQuery.get_settings_manager()

        # Query contracts with end_date within threshold (only CDD or temporary contracts)
        query = (
            Contract.select(Contract, Employee)
            .join(Employee)
            .where(
                (Contract.end_date.is_null(False))
                & (Contract.end_date <= threshold_date)
                & (Contract.status == "active")
            )
        )

        if not include_expired:
            # Only future expirations
            query = query.where(Contract.end_date >= today)

        alerts = []
        for contract in query:
            days_until = (contract.end_date - today).days
            urgency = AlertQuery.calculate_urgency(contract.end_date, category="contract")

            # Get configurable alert level info
            alert_level_obj = settings_manager.get_alert_level("contract", days_until)

            alert = Alert(
                alert_type=AlertType.CONTRACT,
                employee=contract.employee,
                description=f"Contrat {contract.contract_type}",
                expiration_date=contract.end_date,
                days_until=days_until,
                urgency=urgency,
                alert_level=alert_level_obj.label if alert_level_obj else None,
                custom_color=alert_level_obj.color if alert_level_obj else None,
                custom_label=alert_level_obj.label if alert_level_obj else None,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_trial_period_alerts(days_threshold: int = 7) -> List[Alert]:
        """
        Get all trial period ending alerts within threshold.

        Args:
            days_threshold: Maximum days until trial period ends (default: 7 days)

        Returns:
            List of alerts for trial periods ending soon
        """
        from database.connection import database

        if database.is_closed():
            database.connect()

        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        settings_manager = AlertQuery.get_settings_manager()

        # Query contracts with trial_period_ending within threshold
        query = (
            Contract.select(Contract, Employee)
            .join(Employee)
            .where(
                (Contract.trial_period_end.is_null(False))
                & (Contract.trial_period_end <= threshold_date)
                & (Contract.trial_period_end >= today)
                & (Contract.status == "active")
            )
        )

        alerts = []
        for contract in query:
            days_until = (contract.trial_period_end - today).days
            urgency = AlertQuery.calculate_urgency(contract.trial_period_end, category="trial_period")

            # Get configurable alert level info
            alert_level_obj = settings_manager.get_alert_level("trial_period", days_until)

            alert = Alert(
                alert_type=AlertType.CONTRACT,
                employee=contract.employee,
                description=f"Période d'essai {contract.contract_type}",
                expiration_date=contract.trial_period_end,
                days_until=days_until,
                urgency=urgency,
                alert_level=alert_level_obj.label if alert_level_obj else None,
                custom_color=alert_level_obj.color if alert_level_obj else None,
                custom_label=alert_level_obj.label if alert_level_obj else None,
            )
            alerts.append(alert)

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_all_alerts(
        alert_types: Optional[List[AlertType]] = None, days_threshold: int = DEFAULT_ALERT_DAYS, include_expired: bool = True
    ) -> List[Alert]:
        """
        Get all alerts matching criteria.

        Args:
            alert_types: List of alert types to include (None = all)
            days_threshold: Maximum days until expiration (default: DEFAULT_ALERT_DAYS)
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

        # Add contract alerts
        if alert_types is None or AlertType.CONTRACT in alert_types:
            alerts.extend(AlertQuery.get_contract_alerts(days_threshold, include_expired))

        # Sort by days_until (ascending)
        alerts.sort(key=lambda a: a.days_until)

        return alerts

    @staticmethod
    def get_critical_alerts() -> List[Alert]:
        """Get all critical alerts (< ALERT_CRITICAL_DAYS days or expired)."""
        all_alerts = AlertQuery.get_all_alerts(days_threshold=ALERT_CRITICAL_DAYS)
        return [a for a in all_alerts if a.urgency == UrgencyLevel.CRITICAL]

    @staticmethod
    def get_alerts_summary() -> Dict[str, int]:
        """
        Get summary count of alerts by urgency.

        Returns:
            Dictionary with counts for each urgency level
        """
        all_alerts = AlertQuery.get_all_alerts(days_threshold=DEFAULT_ALERT_DAYS)

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
