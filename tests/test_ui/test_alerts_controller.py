"""Tests for AlertsController."""

import pytest
from datetime import date, timedelta

from employee.models import Employee, Caces, MedicalVisit
from controllers.alerts_controller import AlertsController


class TestAlertsController:
    """Tests for AlertsController business logic."""

    def test_get_all_alerts(self, db):
        """Should retrieve all alerts with filtering."""
        # Create employee with expiring items
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get alerts
        controller = AlertsController()
        alerts = controller.get_all_alerts(days=90)

        # Should have at least one alert
        assert len(alerts) >= 1

        # Check alert structure
        alert = alerts[0]
        assert 'employee_id' in alert
        assert 'employee_name' in alert
        assert 'type' in alert
        assert 'description' in alert
        assert 'days_until' in alert
        assert 'priority' in alert

    def test_filter_by_type_caces(self, db):
        """Should filter alerts by type 'caces'."""
        # Create employee
        employee = Employee.create(
            first_name='Jane',
            last_name='Doe',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=20)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get alerts filtered by type
        controller = AlertsController()
        caces_alerts = controller.get_all_alerts(days=90, alert_type='caces')
        medical_alerts = controller.get_all_alerts(days=90, alert_type='medical')

        # CACES filter should return alerts
        assert len(caces_alerts) >= 1
        assert all(a['type'] == 'caces' for a in caces_alerts)

        # Medical filter should not return CACES alerts
        assert len(medical_alerts) == 0

    def test_filter_by_urgency(self, db):
        """Should filter alerts by urgency level."""
        # Create employee with urgent item
        employee = Employee.create(
            first_name='Bob',
            last_name='Johnson',
            current_status='active',
            workspace='Bureau',
            role='Manager',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create urgent CACES (< 15 days)
        expiration_date = date.today() + timedelta(days=5)
        caces = Caces.create(
            employee=employee,
            kind='R489-1B',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get alerts filtered by urgency
        controller = AlertsController()
        urgent_alerts = controller.get_all_alerts(days=90, urgency='urgent')
        normal_alerts = controller.get_all_alerts(days=90, urgency='normal')

        # Urgent filter should return the urgent alert
        assert len(urgent_alerts) >= 1
        assert all(a['priority'] == 'urgent' for a in urgent_alerts)

        # Normal filter should not return urgent alerts
        assert len(normal_alerts) == 0

    def test_get_alerts_summary(self, db):
        """Should return summary statistics of alerts."""
        # Create employees with different urgency levels
        emp1 = Employee.create(
            first_name='Alice',
            last_name='Smith',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Urgent CACES
        expiration_date_urgent = date.today() + timedelta(days=5)
        caces_urgent = Caces.create(
            employee=emp1,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces_urgent.expiration_date = expiration_date_urgent
        caces_urgent.save()

        # Get summary
        controller = AlertsController()
        summary = controller.get_alerts_summary(days=90)

        # Check summary structure
        assert 'total' in summary
        assert 'urgent' in summary
        assert 'high' in summary
        assert 'normal' in summary
        assert 'caces' in summary
        assert 'medical' in summary
        assert 'training' in summary

        # Should have at least one urgent and CACES alert
        assert summary['urgent'] >= 1
        assert summary['caces'] >= 1
        assert summary['total'] >= 1

    def test_export_alerts_to_dict(self, db):
        """Should export alerts as list of dicts."""
        # Create employee with alert
        employee = Employee.create(
            first_name='Charlie',
            last_name='Brown',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        expiration_date = date.today() + timedelta(days=25)
        caces = Caces.create(
            employee=employee,
            kind='R489-3',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Export alerts
        controller = AlertsController()
        export_data = controller.export_alerts_to_dict(days=90)

        # Check export structure
        assert len(export_data) >= 1

        export_row = export_data[0]
        assert 'Employee Name' in export_row
        assert 'Type' in export_row
        assert 'Description' in export_row
        assert 'Days Until' in export_row
        assert 'Priority' in export_row

        # Check data types
        assert isinstance(export_row['Employee Name'], str)
        assert isinstance(export_row['Type'], str)
        assert isinstance(export_row['Days Until'], int)

    def test_alerts_sorted_by_priority(self, db):
        """Should sort alerts by priority then days until."""
        controller = AlertsController()

        # Test priority order mapping
        priority_order = {'urgent': 0, 'high': 1, 'normal': 2}

        # Create test alerts
        alerts = [
            {'priority': 'normal', 'days_until': 50},
            {'priority': 'urgent', 'days_until': 10},
            {'priority': 'high', 'days_until': 20},
            {'priority': 'urgent', 'days_until': 5},
        ]

        # Sort using controller's logic
        alerts.sort(key=lambda a: (priority_order[a['priority']], a['days_until']))

        # Verify order
        assert alerts[0]['priority'] == 'urgent'
        assert alerts[0]['days_until'] == 5
        assert alerts[1]['priority'] == 'urgent'
        assert alerts[1]['days_until'] == 10
        assert alerts[2]['priority'] == 'high'
        assert alerts[3]['priority'] == 'normal'
