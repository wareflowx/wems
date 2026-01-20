"""Alerts controller - business logic for alerts view."""

from typing import Dict, List, Any
from datetime import date, timedelta

from employee import queries


class AlertsController:
    """
    Controller for Alerts view.

    Provides advanced filtering and export functionality for alerts.
    """

    def __init__(self):
        """Initialize alerts controller."""
        pass

    def get_all_alerts(
        self,
        days: int = 90,
        alert_type: str = "all",
        urgency: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Get all alerts with optional filtering.

        Args:
            days: Number of days to look ahead (default: 90)
            alert_type: Filter by type ('all', 'caces', 'medical', 'training')
            urgency: Filter by urgency ('all', 'urgent', 'high', 'normal')

        Returns:
            List of alert dictionaries:
            [
                {
                    'employee_id': str,
                    'employee_name': str,
                    'type': str,
                    'description': str,
                    'days_until': int,
                    'priority': str,
                }
            ]
        """
        # Get expiring items by type
        alerts_by_employee = queries.get_expiring_items_by_type(days=days)
        formatted_alerts = []

        for emp_id, data in alerts_by_employee.items():
            emp = data['employee']

            # Process CACES alerts
            if alert_type in ['all', 'caces']:
                for caces in data['caces']:
                    priority = self._get_priority_level(caces.days_until_expiration)
                    if urgency == 'all' or priority == urgency:
                        formatted_alerts.append({
                            'employee_id': str(emp.id),
                            'employee_name': emp.full_name,
                            'type': 'caces',
                            'description': f"CACES {caces.kind}",
                            'days_until': caces.days_until_expiration,
                            'priority': priority,
                        })

            # Process medical visit alerts
            if alert_type in ['all', 'medical']:
                for visit in data['medical_visits']:
                    priority = self._get_priority_level(visit.days_until_expiration)
                    if visit.visit_result == 'unfit':
                        priority = 'urgent'
                    if urgency == 'all' or priority == urgency:
                        formatted_alerts.append({
                            'employee_id': str(emp.id),
                            'employee_name': emp.full_name,
                            'type': 'medical',
                            'description': f"Medical visit ({visit.visit_kind})",
                            'days_until': visit.days_until_expiration,
                            'priority': priority,
                        })

            # Process training alerts
            if alert_type in ['all', 'training']:
                for training in data['trainings']:
                    days_until = training.days_until_expiration or 9999
                    priority = self._get_priority_level(days_until)
                    if urgency == 'all' or priority == urgency:
                        formatted_alerts.append({
                            'employee_id': str(emp.id),
                            'employee_name': emp.full_name,
                            'type': 'training',
                            'description': f"Training: {training.title}",
                            'days_until': days_until,
                            'priority': priority,
                        })

        # Sort by priority and days_until
        priority_order = {'urgent': 0, 'high': 1, 'normal': 2}
        formatted_alerts.sort(
            key=lambda a: (priority_order[a['priority']], a['days_until'])
        )

        return formatted_alerts

    def get_alerts_summary(self, days: int = 90) -> Dict[str, int]:
        """
        Get summary count of alerts by type and urgency.

        Args:
            days: Number of days to look ahead

        Returns:
            Dictionary with counts:
            {
                'total': int,
                'urgent': int,
                'high': int,
                'normal': int,
                'caces': int,
                'medical': int,
                'training': int,
            }
        """
        alerts = self.get_all_alerts(days=days)

        summary = {
            'total': len(alerts),
            'urgent': 0,
            'high': 0,
            'normal': 0,
            'caces': 0,
            'medical': 0,
            'training': 0,
        }

        for alert in alerts:
            summary[alert['priority']] += 1
            summary[alert['type']] += 1

        return summary

    def export_alerts_to_dict(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Export alerts as list of dicts (for Excel export).

        Args:
            days: Number of days to look ahead

        Returns:
            List of dictionaries ready for export
        """
        alerts = self.get_all_alerts(days=days)

        export_data = []
        for alert in alerts:
            export_data.append({
                'Employee Name': alert['employee_name'],
                'Type': alert['type'].capitalize(),
                'Description': alert['description'],
                'Days Until': alert['days_until'],
                'Priority': alert['priority'].capitalize(),
            })

        return export_data

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
            return 'urgent'
        elif days_until < 30:
            return 'high'
        else:
            return 'normal'
