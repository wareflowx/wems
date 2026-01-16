"""Tests for OnlineTraining model."""

import pytest
from datetime import date

from employee.models import OnlineTraining


class TestOnlineTrainingCreation:
    """Tests for OnlineTraining model creation."""

    def test_online_training_with_expiration(self, online_training):
        """Test creating training with validity period."""
        assert online_training.validity_months == 12
        assert online_training.expiration_date is not None

    def test_online_training_permanent(self, permanent_training):
        """Test creating permanent (non-expiring) training."""
        assert permanent_training.validity_months is None
        assert permanent_training.expiration_date is None


class TestOnlineTrainingExpiration:
    """Tests for OnlineTraining expiration calculation."""

    def test_online_training_expiration_calculation(self, online_training):
        """Test that expiration is calculated correctly."""
        # Completion: 2023-03-01, validity: 12 months
        # Expiration: 2024-03-01
        assert online_training.expiration_date == date(2024, 3, 1)

    def test_online_training_month_overflow(self, db, sample_employee):
        """Test month overflow in expiration calculation."""
        # Completion in November, validity 3 months
        # Should correctly roll over to next year (February)
        training = OnlineTraining.create(
            employee=sample_employee,
            title='Year End Training',
            completion_date=date(2023, 11, 15),
            validity_months=3,
            certificate_path='/documents/training/year-end.pdf'
        )

        assert training.expiration_date == date(2024, 2, 15)


class TestOnlineTrainingProperties:
    """Tests for OnlineTraining computed properties."""

    def test_online_training_expires_property(self, online_training):
        """Test the expires property."""
        assert online_training.expires is True

    def test_online_training_does_not_expire(self, permanent_training):
        """Test the expires property for permanent training."""
        assert permanent_training.expires is False

    def test_online_training_status_permanent(self, permanent_training):
        """Test status property for permanent training."""
        assert permanent_training.status == 'permanent'

    def test_online_training_permanent_days_until_expiration(self, permanent_training):
        """Test days_until_expiration returns None for permanent."""
        assert permanent_training.days_until_expiration is None


class TestOnlineTrainingCascadeDelete:
    """Tests for CASCADE delete behavior."""

    def test_deleting_employee_deletes_trainings(self, sample_employee, online_training):
        """Test that deleting employee CASCADE deletes their trainings."""
        from employee.models import Employee

        employee_id = sample_employee.id
        training_id = online_training.id

        sample_employee.delete_instance()

        assert Employee.get_or_none(Employee.id == employee_id) is None
        assert OnlineTraining.get_or_none(OnlineTraining.id == training_id) is None
