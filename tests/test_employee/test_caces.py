"""Tests for Caces model."""

import pytest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from employee.models import Caces


class TestCacesExpiration:
    """Tests for CACES expiration calculation."""

    def test_caces_auto_calculates_expiration_r489_1a(self, sample_caces):
        """Test that R489-1A automatically calculates 5-year expiration."""
        # Created on 2023-01-01, should expire on 2028-01-01
        assert sample_caces.expiration_date == date(2028, 1, 1)

    def test_caces_auto_calculates_expiration_r489_5(self, db, sample_employee):
        """Test that R489-5 automatically calculates 10-year expiration."""
        caces = Caces.create(
            employee=sample_employee,
            kind='R489-5',  # 10 year validity
            completion_date=date(2023, 1, 1),
            document_path='/documents/caces/r489-5.pdf'
        )

        assert caces.expiration_date == date(2033, 1, 1)

    def test_caces_expiration_handles_leap_years(self, db, sample_employee):
        """Test that expiration calculation handles leap years correctly."""
        # Feb 29, 2020 is a leap year
        caces = Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=date(2020, 2, 29),  # Leap year!
            document_path='/documents/caces/leap.pdf'
        )

        # 5 years later should be Feb 28, 2025 (not a leap year)
        assert caces.expiration_date == date(2025, 2, 28)

    def test_caces_can_override_expiration(self, db, sample_employee):
        """Test that expiration_date can be manually set."""
        custom_expiration = date(2030, 12, 31)
        caces = Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=date(2023, 1, 1),
            expiration_date=custom_expiration,  # Manual override
            document_path='/documents/caces/custom.pdf'
        )

        assert caces.expiration_date == custom_expiration


class TestCacesProperties:
    """Tests for CACES computed properties."""

    def test_caces_is_expired_property(self, expired_caces):
        """Test the is_expired property for expired certification."""
        assert expired_caces.is_expired is True

    def test_caces_is_not_expired(self, sample_caces):
        """Test the is_expired property for valid certification."""
        assert sample_caces.is_expired is False

    def test_caces_days_until_expiration(self, sample_caces):
        """Test the days_until_expiration property."""
        # Created 2023-01-01, expires 2028-01-01
        # As of 2026, should be roughly 2 years * 365 days remaining
        days = sample_caces.days_until_expiration
        assert 700 <= days <= 730  # Allow for leap years and exact date

    def test_caces_days_until_expiration_negative_when_expired(self, expired_caces):
        """Test that days_until_expiration is negative when expired."""
        assert expired_caces.days_until_expiration < 0

    def test_caces_status_valid(self, sample_caces):
        """Test status property returns 'valid' for valid CACES."""
        assert sample_caces.status == 'valid'

    def test_caces_status_expired(self, expired_caces):
        """Test status property returns 'expired' for expired CACES."""
        assert expired_caces.status == 'expired'

    def test_caces_status_critical(self, db, sample_employee):
        """Test status property returns 'critical' for soon-to-expire."""
        # Create CACES that expires in 15 days
        completion = date.today() - relativedelta(years=5) + timedelta(days=15)
        caces = Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=completion,
            document_path='/documents/caces/soon.pdf'
        )

        assert caces.status == 'critical'


class TestCacesQueries:
    """Tests for CACES class methods."""

    def test_caces_expiring_soon(self, db, sample_employee):
        """Test getting certifications expiring within X days."""
        # Create expiring certification (20 days from now)
        expiring_date = date.today() + timedelta(days=20)
        caces = Caces.create(
            employee=sample_employee,
            kind='R489-1A',
            completion_date=expiring_date - relativedelta(years=5),
            document_path='/documents/caces/expiring.pdf'
        )

        expiring = list(Caces.expiring_soon(days=30))
        assert len(expiring) >= 1

    def test_caces_expired_query(self, expired_caces, sample_caces):
        """Test getting only expired certifications."""
        expired = list(Caces.expired())

        assert expired_caces in expired
        assert sample_caces not in expired

    def test_caces_by_kind(self, sample_caces):
        """Test filtering by CACES kind."""
        r489_1a_caces = list(Caces.by_kind('R489-1A'))
        assert sample_caces in r489_1a_caces


class TestCacesCascadeDelete:
    """Tests for CASCADE delete behavior."""

    def test_deleting_employee_deletes_caces(self, sample_employee, sample_caces):
        """Test that deleting employee CASCADE deletes their CACES."""
        from employee.models import Employee

        employee_id = sample_employee.id
        caces_id = sample_caces.id

        # Delete employee
        sample_employee.delete_instance()

        # Both should be deleted
        assert Employee.get_or_none(Employee.id == employee_id) is None
        assert Caces.get_or_none(Caces.id == caces_id) is None
