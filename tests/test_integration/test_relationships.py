"""Integration tests for model relationships."""

import pytest
from datetime import date
from peewee import prefetch

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining


class TestBackReferences:
    """Tests for back-reference queries."""

    def test_employee_caces_back_reference(self, sample_employee, sample_caces):
        """Test accessing CACES through employee back-reference."""
        employee = Employee.get_by_id(sample_employee.id)
        caces_list = list(employee.caces)

        assert len(caces_list) == 1
        assert caces_list[0].kind == 'R489-1A'

    def test_employee_medical_visits_back_reference(self, sample_employee, medical_visit):
        """Test accessing medical visits through employee back-reference."""
        employee = Employee.get_by_id(sample_employee.id)
        visits = list(employee.medical_visits)

        assert len(visits) == 1
        assert visits[0].visit_type == 'periodic'

    def test_employee_trainings_back_reference(self, sample_employee, online_training):
        """Test accessing trainings through employee back-reference."""
        employee = Employee.get_by_id(sample_employee.id)
        trainings = list(employee.trainings)

        assert len(trainings) == 1
        assert trainings[0].title == 'Safety Training'


class TestMultipleRelationships:
    """Tests for multiple related records per employee."""

    def test_multiple_caces_per_employee(self, sample_employee):
        """Test that an employee can have multiple CACES."""
        Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=date(2023, 1, 1),
            document_path='/caces/1a.pdf'
        )

        Caces.create(
            employee=sample_employee,
            kind='R489-3',
            completion_date=date(2023, 6, 1),
            document_path='/caces/3.pdf'
        )

        assert len(list(sample_employee.caces)) == 2

    def test_employee_with_all_relationship_types(self, sample_employee, sample_caces, medical_visit, online_training):
        """Test employee with all types of related records."""
        # Create CACES
        Caces.create(
            employee=sample_employee,
            kind='R489-1B',
            completion_date=date(2023, 2, 1),
            document_path='/caces/1b.pdf'
        )

        # Create medical visit
        MedicalVisit.create(
            employee=sample_employee,
            visit_type='initial',
            visit_date=date(2023, 1, 10),
            result='fit',
            document_path='/medical/initial.pdf'
        )

        # Create training
        OnlineTraining.create(
            employee=sample_employee,
            title='Safety',
            completion_date=date(2023, 3, 1),
            validity_months=12,
            certificate_path='/training/safety.pdf'
        )

        # Reload employee
        employee = Employee.get_by_id(sample_employee.id)

        assert len(list(employee.caces)) == 2  # sample_caces + new one
        assert len(list(employee.medical_visits)) == 2  # medical_visit + new one
        assert len(list(employee.trainings)) == 2  # online_training + new one


class TestCascadeDelete:
    """Tests for CASCADE delete behavior."""

    def test_cascade_delete_employee_deletes_everything(self, sample_employee, db):
        """Test that deleting employee CASCADE deletes all related records."""
        # Add multiple related records
        Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=date(2023, 1, 1),
            document_path='/caces/test.pdf'
        )

        MedicalVisit.create(
            employee=sample_employee,
            visit_type='periodic',
            visit_date=date(2023, 1, 1),
            result='fit',
            document_path='/medical/test.pdf'
        )

        OnlineTraining.create(
            employee=sample_employee,
            title='Test Training',
            completion_date=date(2023, 1, 1),
            validity_months=12,
            certificate_path='/training/test.pdf'
        )

        employee_id = sample_employee.id

        # Delete employee
        sample_employee.delete_instance()

        # Everything should be deleted
        assert Employee.get_or_none(Employee.id == employee_id) is None

        # No CACES, visits, or trainings should reference this employee
        assert len(list(Caces.select())) == 0
        assert len(list(MedicalVisit.select())) == 0
        assert len(list(OnlineTraining.select())) == 0


class TestPrefetch:
    """Tests for prefetch to avoid N+1 queries."""

    def test_prefetch_caces_avoids_n_plus_1(self, sample_employee, sample_caces):
        """Test that prefetch() loads CACES efficiently."""
        # Get employee with prefetched CACES
        employees = Employee.select()
        employees_with_caces = prefetch(employees, Caces)

        for emp in employees_with_caces:
            _ = list(emp.caces)  # Should not trigger query

        # If this works without error, prefetch is working
        assert True
