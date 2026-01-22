"""Dashboard controller - business logic for dashboard view."""

from typing import Any, Dict, List

from employee import calculations, queries
from employee.models import Employee


class DashboardController:
    """
    Controller for Dashboard view.

    Orchestrates data fetching from business logic layer
    and formats it for UI consumption.
    """

    def get_statistics(self) -> Dict[str, int]:
        """
        Get dashboard statistics.

        Returns:
            Dictionary with:
                - total_employees: Total number of employees
                - active_employees: Number of active employees
                - expiring_caces: Number of CACES expiring within 30 days
                - expiring_visits: Number of medical visits expiring within 30 days
                - unfit_employees: Number of employees with unfit status
        """
        return queries.get_dashboard_statistics()

    def get_alerts(self, days: int = 30) -> Dict[int, Dict[str, Any]]:
        """
        Get alerts grouped by employee.

        Args:
            days: Number of days to look ahead (default: 30)

        Returns:
            Dictionary mapping employee_id to alert data:
            {
                employee_id: {
                    'employee': Employee,
                    'caces': [Caces, ...],
                    'medical_visits': [MedicalVisit, ...],
                    'trainings': [OnlineTraining, ...]
                }
            }
        """
        return queries.get_expiring_items_by_type(days=days)

    def get_compliance_percentage(self) -> int:
        """
        Calculate global compliance percentage.

        Returns:
            Percentage of compliant employees (0-100).
            An employee is considered compliant if their
            compliance score is >= 70%.
        """
        employees = list(Employee.select())

        if not employees:
            return 100

        compliant_count = 0
        for emp in employees:
            score_data = calculations.calculate_compliance_score(emp)
            if score_data["score"] >= 70:
                compliant_count += 1

        percentage = int((compliant_count / len(employees)) * 100)
        return percentage

    def get_total_alerts_count(self, days: int = 30) -> int:
        """
        Get total number of active alerts.

        Args:
            days: Number of days to look ahead (default: 30)

        Returns:
            Total count of items expiring within the period.
        """
        stats = self.get_statistics()
        return stats["expiring_caces"] + stats["expiring_visits"] + stats["unfit_employees"]

    def format_alerts_for_ui(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Format alerts for UI display.

        Args:
            days: Number of days to look ahead (default: 30)
            limit: Maximum number of alerts to return (default: 10)

        Returns:
            List of alert dictionaries sorted by urgency:
            [
                {
                    'employee_id': int,
                    'employee_name': str,
                    'type': 'caces' | 'medical' | 'training',
                    'description': str,
                    'days_until': int,
                    'priority': 'urgent' | 'high' | 'normal',
                }
            ]
        """
        alerts_by_employee = self.get_alerts(days=days)
        formatted_alerts = []

        for emp_id, data in alerts_by_employee.items():
            emp = data["employee"]

            # Process CACES alerts
            for caces in data["caces"]:
                formatted_alerts.append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "type": "caces",
                        "description": f"CACES {caces.kind}",
                        "days_until": caces.days_until_expiration,
                        "priority": self._get_priority_level(caces.days_until_expiration),
                    }
                )

            # Process medical visit alerts
            for visit in data["medical_visits"]:
                formatted_alerts.append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "type": "medical",
                        "description": "Medical visit",
                        "days_until": visit.days_until_expiration,
                        "priority": self._get_priority_level(visit.days_until_expiration),
                    }
                )

            # Process training alerts
            for training in data["trainings"]:
                formatted_alerts.append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "type": "training",
                        "description": f"Training: {training.title}",
                        "days_until": training.days_until_expiration or 9999,
                        "priority": self._get_priority_level(training.days_until_expiration or 9999),
                    }
                )

        # Sort by priority and days_until
        priority_order = {"urgent": 0, "high": 1, "normal": 2}
        formatted_alerts.sort(key=lambda a: (priority_order[a["priority"]], a["days_until"]))

        return formatted_alerts[:limit]

    def _get_priority_level(self, days_until: int) -> str:
        """
        Convert days until expiration to priority level.

        Args:
            days_until: Days until expiration (can be negative for expired)

        Returns:
            'urgent' if expired or < 15 days
            'high' if < 30 days
            'normal' if < 90 days
        """
        if days_until < 15:
            return "urgent"
        elif days_until < 30:
            return "high"
        else:
            return "normal"
