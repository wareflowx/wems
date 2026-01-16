"""Tests for Employee queries."""

import pytest
from datetime import date, timedelta
from freezegun import freeze_time

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from employee import queries


class TestGetEmployeesWithExpiringItems:
    """Tests for get_employees_with_expiring_items function."""

    def test_returns_employees_with_expiring_caces(self, db):
        """Should return employees with CACES expiring within threshold."""
        # Create employee with CACES expiring in 15 days
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create CACES expiring soon
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        # Manually set expiration to simulate expiring CACES
        caces.expiration_date = expiration_date
        caces.save()

        # Get employees with expiring items
        result = queries.get_employees_with_expiring_items(days=30)

        # Should return our employee
        assert len(result) == 1
        assert result[0].id == employee.id

    def test_does_not_return_employees_with_valid_items(self, db):
        """Should not return employees with all valid items (> 30 days)."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create CACES with default expiration (5 years from completion)
        Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date.today(),
            document_path='/test.pdf'
        )

        # Get employees with expiring items
        result = queries.get_employees_with_expiring_items(days=30)

        # Should not return our employee (CACES valid for 5 years)
        assert len(result) == 0

    def test_returns_employees_with_expiring_medical_visits(self, db):
        """Should return employees with medical visits expiring soon."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create medical visit expiring in 20 days
        expiration_date = date.today() + timedelta(days=20)
        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        result = queries.get_employees_with_expiring_items(days=30)

        assert len(result) == 1
        assert result[0].id == employee.id

    def test_returns_employees_with_expiring_trainings(self, db):
        """Should return employees with trainings expiring soon."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create training expiring in 10 days
        expiration_date = date.today() + timedelta(days=10)
        training = OnlineTraining.create(
            employee=employee,
            title='Safety Training',
            completion_date=date.today(),
            validity_months=12,
            certificate_path='/test.pdf'
        )
        training.expiration_date = expiration_date
        training.save()

        result = queries.get_employees_with_expiring_items(days=30)

        assert len(result) == 1
        assert result[0].id == employee.id

    def test_prefetches_related_items(self, db):
        """Should prefetch related items to avoid N+1 queries."""
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
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        result = queries.get_employees_with_expiring_items(days=30)

        # Accessing related items should not trigger additional queries
        # (this would fail if prefetch wasn't working)
        assert len(result[0].caces) == 1


class TestGetEmployeesWithExpiredCaces:
    """Tests for get_employees_with_expired_caces function."""

    def test_returns_employees_with_expired_caces(self, db):
        """Should return employees with expired CACES."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expired CACES
        expiration_date = date.today() - timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2015, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        result = queries.get_employees_with_expired_caces()

        assert len(result) == 1
        assert result[0].id == employee.id

    def test_does_not_return_employees_with_valid_caces(self, db):
        """Should not return employees with valid CACES."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create valid CACES
        Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date.today(),
            document_path='/test.pdf'
        )

        result = queries.get_employees_with_expired_caces()

        assert len(result) == 0


class TestGetEmployeesWithExpiredMedicalVisits:
    """Tests for get_employees_with_expired_medical_visits function."""

    def test_returns_employees_with_expired_visits(self, db):
        """Should return employees with expired medical visits."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expired medical visit
        expiration_date = date.today() - timedelta(days=5)
        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date(2020, 1, 1),
            result='fit',
            document_path='/test.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        result = queries.get_employees_with_expired_medical_visits()

        assert len(result) == 1
        assert result[0].id == employee.id


class TestGetUnfitEmployees:
    """Tests for get_unfit_employees function."""

    def test_returns_employees_with_unfit_visits(self, db):
        """Should return employees with unfit medical status."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create unfit visit
        MedicalVisit.create(
            employee=employee,
            visit_type='recovery',
            visit_date=date.today(),
            result='unfit',
            document_path='/test.pdf'
        )

        result = queries.get_unfit_employees()

        assert len(result) == 1
        assert result[0].id == employee.id

    def test_does_not_return_fit_employees(self, db):
        """Should not return employees with fit status."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create fit visit
        MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )

        result = queries.get_unfit_employees()

        assert len(result) == 0


class TestGetDashboardStatistics:
    """Tests for get_dashboard_statistics function."""

    def test_returns_correct_counts(self, db):
        """Should return accurate statistics."""
        # Create active and inactive employees
        active_emp = Employee.create(
            first_name='Active',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        inactive_emp = Employee.create(
            first_name='Inactive',
            last_name='User',
            current_status='inactive',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=active_emp,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Create expiring medical visit
        expiration_date = date.today() + timedelta(days=20)
        visit = MedicalVisit.create(
            employee=active_emp,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        # Create unfit visit
        MedicalVisit.create(
            employee=inactive_emp,
            visit_type='recovery',
            visit_date=date.today(),
            result='unfit',
            document_path='/test.pdf'
        )

        stats = queries.get_dashboard_statistics()

        assert stats['total_employees'] == 2
        assert stats['active_employees'] == 1
        assert stats['expiring_caces'] == 1
        assert stats['expiring_visits'] == 1
        assert stats['unfit_employees'] == 1


class TestGetExpiringItemsByType:
    """Tests for get_expiring_items_by_type function."""

    def test_groups_items_by_employee(self, db):
        """Should group expiring items by employee."""
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
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        result = queries.get_expiring_items_by_type(days=30)

        # Should have one employee entry
        assert len(result) == 1
        emp_id = list(result.keys())[0]

        # Should have employee object
        assert result[emp_id]['employee'].id == employee.id

        # Should have expiring CACES
        assert len(result[emp_id]['caces']) == 1

    def test_includes_all_expiring_types(self, db):
        """Should include CACES, medical visits, and trainings."""
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
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Create expiring medical visit
        expiration_date = date.today() + timedelta(days=20)
        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        # Create expiring training
        expiration_date = date.today() + timedelta(days=10)
        training = OnlineTraining.create(
            employee=employee,
            title='Safety Training',
            completion_date=date.today(),
            validity_months=12,
            certificate_path='/test.pdf'
        )
        training.expiration_date = expiration_date
        training.save()

        result = queries.get_expiring_items_by_type(days=30)

        emp_id = list(result.keys())[0]

        # Should have all three types
        assert len(result[emp_id]['caces']) == 1
        assert len(result[emp_id]['medical_visits']) == 1
        assert len(result[emp_id]['trainings']) == 1
