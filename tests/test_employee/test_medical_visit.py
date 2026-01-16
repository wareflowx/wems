"""Tests for MedicalVisit model."""

import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

from employee.models import MedicalVisit


class TestMedicalVisitExpiration:
    """Tests for MedicalVisit expiration calculation."""

    def test_medical_visit_auto_calculates_expiration_initial(self, medical_visit):
        """Test that initial visit gets 2-year expiration."""
        # Visit date: 2023-06-15
        # Expiration: 2025-06-15 (2 years)
        assert medical_visit.expiration_date == date(2025, 6, 15)

    def test_medical_visit_auto_calculates_expiration_periodic(self, db, sample_employee):
        """Test that periodic visit gets 2-year expiration."""
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type='periodic',
            visit_date=date(2023, 3, 1),
            result='fit',
            document_path='/documents/medical/periodic.pdf'
        )

        assert visit.expiration_date == date(2025, 3, 1)

    def test_medical_visit_auto_calculates_expiration_recovery(self, unfit_visit):
        """Test that recovery visit gets 1-year expiration."""
        # Visit date: 2023-01-01
        # Expiration: 2024-01-01 (1 year)
        assert unfit_visit.expiration_date == date(2024, 1, 1)


class TestMedicalVisitProperties:
    """Tests for MedicalVisit computed properties."""

    def test_medical_visit_is_fit_property(self, medical_visit):
        """Test the is_fit property."""
        assert medical_visit.is_fit is True

        medical_visit.result = 'unfit'
        assert medical_visit.is_fit is False

    def test_medical_visit_has_restrictions_property(self, db, sample_employee):
        """Test the has_restrictions property."""
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type='periodic',
            visit_date=date(2023, 1, 1),
            result='fit_with_restrictions',
            document_path='/documents/medical/restrictions.pdf'
        )

        assert visit.has_restrictions is True

    def test_medical_visit_has_no_restrictions_when_fit(self, medical_visit):
        """Test has_restrictions is False when fit."""
        assert medical_visit.has_restrictions is False


class TestMedicalVisitCascadeDelete:
    """Tests for CASCADE delete behavior."""

    def test_deleting_employee_deletes_medical_visits(self, sample_employee, medical_visit):
        """Test that deleting employee CASCADE deletes their medical visits."""
        from employee.models import Employee

        employee_id = sample_employee.id
        visit_id = medical_visit.id

        sample_employee.delete_instance()

        assert Employee.get_or_none(Employee.id == employee_id) is None
        assert MedicalVisit.get_or_none(MedicalVisit.id == visit_id) is None
