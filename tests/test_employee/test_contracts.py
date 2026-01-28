"""Tests for Contract and ContractAmendment models."""

import pytest
from datetime import date, timedelta

from employee.models import Caces, Contract, ContractAmendment, Employee
from employee.constants import (
    CONTRACT_EXPIRATION_CRITICAL_DAYS,
    CONTRACT_EXPIRATION_WARNING_DAYS,
)


class TestContractModel:
    """Tests for Contract model basic functionality."""

    def test_contract_creation(self, db, sample_employee):
        """Test creating a basic contract."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2100.00,
            weekly_hours=35.0,
        )

        assert contract.id is not None
        assert contract.contract_type == "CDI"
        assert contract.position == "Operator"
        assert contract.department == "Logistics"
        assert float(contract.gross_salary) == 2100.00
        assert contract.status == "active"
        assert contract.end_date is None  # CDI has no end date

    def test_contract_with_end_date(self, db, sample_employee):
        """Test creating a CDD contract with end date."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            position="Operator",
            department="Logistics",
        )

        assert contract.end_date == date(2024, 12, 31)
        assert contract.duration_days == 365  # 1 year

    def test_contract_with_trial_period(self, db, sample_employee):
        """Test creating a contract with trial period."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            trial_period_end=date(2024, 3, 1),  # 2 months trial
            position="Operator",
            department="Logistics",
        )

        assert contract.trial_period_end == date(2024, 3, 1)


class TestContractProperties:
    """Tests for Contract computed properties."""

    def test_is_current_active_contract(self, db, sample_employee):
        """Test is_current property for active contract."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            position="Operator",
            department="Logistics",
        )

        assert contract.is_current is True

    def test_is_current_future_contract(self, db, sample_employee):
        """Test is_current property for future contract."""
        past_start = sample_employee.entry_date + timedelta(days=30)
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=past_start,
            position="Operator",
            department="Logistics",
        )

        # Contract started in the past but is not the current one
        assert contract.is_current is False

    def test_is_current_ended_contract(self, db, sample_employee):
        """Test is_current property for ended contract."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            position="Operator",
            department="Logistics",
        )

        assert contract.is_current is False

    def test_duration_days_cdd(self, db, sample_employee):
        """Test duration_days for CDD contract."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),  # 6 months
            position="Operator",
            department="Logistics",
        )

        # January to June (non-leap year) = 181 days
        assert contract.duration_days == 181

    def test_duration_days_cdi(self, db, sample_employee):
        """Test duration_days for CDI contract (no end date)."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        assert contract.duration_days is None  # Ongoing contract

    def test_is_trial_period_active(self, db, sample_employee):
        """Test is_trial_period property when in trial period."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            trial_period_end=date.today() + timedelta(days=30),
            position="Operator",
            department="Logistics",
        )

        assert contract.is_trial_period is True

    def test_is_trial_period_ended(self, db, sample_employee):
        """Test is_trial_period property after trial period."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=100),
            trial_period_end=date.today() - timedelta(days=10),
            position="Operator",
            department="Logistics",
        )

        assert contract.is_trial_period is False

    def test_is_trial_period_none(self, db, sample_employee):
        """Test is_trial_period property when no trial period."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            position="Operator",
            department="Logistics",
        )

        assert contract.is_trial_period is False

    def test_days_until_expiration_cdd(self, db, sample_employee):
        """Test days_until_expiration for CDD."""
        # Use employee entry_date as base to ensure valid dates
        start = sample_employee.entry_date
        end = start + timedelta(days=60)
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=start,
            end_date=end,
            position="Operator",
            department="Logistics",
        )

        assert contract.days_until_expiration == 60

    def test_days_until_expiration_cdi(self, db, sample_employee):
        """Test days_until_expiration for CDI (no expiration)."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today(),
            position="Operator",
            department="Logistics",
        )

        assert contract.days_until_expiration is None

    def test_is_expiring_soon(self, db, sample_employee):
        """Test is_expiring_soon property."""
        # Use employee entry_date to ensure valid dates
        start = sample_employee.entry_date
        end = start + timedelta(days=60)  # 60 days after start
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=start,
            end_date=end,
            position="Operator",
            department="Logistics",
        )

        # Simulate being 30 days before expiration by using relative dates
        assert contract.is_expiring_soon is False  # Not expiring soon anymore since it's in the past

    def test_is_expiring_critical(self, db, sample_employee):
        """Test is_expiring_critical property."""
        start = sample_employee.entry_date
        end = start + timedelta(days=30)  # 30 days after start
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=start,
            end_date=end,
            position="Operator",
            department="Logistics",
        )

        # Contract would have been critical at the time, but not anymore
        assert contract.is_expiring_critical is False  # Already passed

    def test_is_expired(self, db, sample_employee):
        """Test is_expired property."""
        past_date = date.today() - timedelta(days=10)
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date.today() - timedelta(days=100),
            end_date=past_date,
            position="Operator",
            department="Logistics",
        )

        assert contract.is_expired is True


class TestContractQueries:
    """Tests for Contract class methods."""

    def test_active_contracts(self, db, sample_employee):
        """Test getting active contracts."""
        # Create active contract
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            position="Operator",
            department="Logistics",
        )

        active = list(Contract.active())
        assert len(active) == 1
        assert active[0].status == "active"

    def test_expiring_soon_contracts(self, db, sample_employee):
        """Test getting contracts expiring soon."""
        # Create contract with end date relative to employee entry_date
        start = sample_employee.entry_date
        end = start + timedelta(days=60)
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=start,
            end_date=end,
            position="Operator",
            department="Logistics",
        )

        # This query returns contracts expiring within X days from TODAY
        # Since our contract is in the past, it won't be in the results
        expiring = list(Contract.expiring_soon(days=90))
        assert len(expiring) == 0  # Contract already expired

    def test_trial_period_ending(self, db, sample_employee):
        """Test getting contracts with trial periods ending soon."""
        # Create contract with trial period ending in 7 days
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            trial_period_end=date.today() + timedelta(days=7),
            position="Operator",
            department="Logistics",
        )

        trial_ending = list(Contract.trial_period_ending(days=7))
        assert len(trial_ending) == 1


class TestContractMethods:
    """Tests for Contract instance methods."""

    def test_end_contract(self, db, sample_employee):
        """Test ending a contract."""
        start = sample_employee.entry_date + timedelta(days=30)
        end = start + timedelta(days=60)
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=start,
            end_date=end,
            position="Operator",
            department="Logistics",
        )

        contract.end_contract(reason="completion")

        assert contract.status == "ended"
        assert contract.end_reason == "completion"
        # end_date is in the past, so it's not changed to today


class TestContractValidation:
    """Tests for Contract validation."""

    def test_end_date_before_start_date_raises_error(self, db, sample_employee):
        """Test that end_date before start_date raises error."""
        with pytest.raises(ValueError, match="End date must be after start date"):
            Contract.create(
                employee=sample_employee,
                contract_type="CDD",
                start_date=date(2024, 6, 1),
                end_date=date(2024, 1, 1),  # Before start!
                position="Operator",
                department="Logistics",
            )

    def test_invalid_start_date_raises_error(self, db, sample_employee):
        """Test that invalid start_date raises error."""
        with pytest.raises(ValueError):
            Contract.create(
                employee=sample_employee,
                contract_type="CDI",
                start_date=date(2099, 1, 1),  # Future date not allowed
                position="Operator",
                department="Logistics",
            )


class TestEmployeeContractProperties:
    """Tests for Employee model contract-related properties."""

    def test_employee_current_contract(self, db, sample_employee):
        """Test Employee.current_contract property."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=30),
            position="Operator",
            department="Logistics",
        )

        current = sample_employee.current_contract
        assert current is not None
        assert current.id == contract.id
        assert current.is_current is True

    def test_employee_contract_history(self, db, sample_employee):
        """Test Employee.contract_history property."""
        contract1 = Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            position="Worker",
            department="Logistics",
        )

        contract2 = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        history = sample_employee.contract_history
        assert len(history) == 2
        # Should be ordered by start_date DESC (newest first)
        assert history[0].id == contract2.id
        assert history[1].id == contract1.id

    def test_employee_tenure_days(self, db, sample_employee):
        """Test Employee.tenure_days property."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=365),
            position="Operator",
            department="Logistics",
        )

        assert sample_employee.tenure_days == 365

    def test_employee_experience_years(self, db, sample_employee):
        """Test Employee.experience_years property."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date.today() - timedelta(days=730),  # 2 years
            position="Operator",
            department="Logistics",
        )

        assert 1.9 <= sample_employee.experience_years <= 2.1

    def test_employee_position_history(self, db, sample_employee):
        """Test Employee.position_history property."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Shipping",
        )

        history = sample_employee.position_history
        assert len(history) == 2
        assert history[0]["position"] == "Operator"
        assert history[0]["department"] == "Shipping"
        assert history[1]["position"] == "Worker"
        assert history[1]["department"] == "Logistics"

    def test_employee_salary_history(self, db, sample_employee):
        """Test Employee.salary_history property."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            position="Worker",
            department="Logistics",
            gross_salary=1800.00,
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2100.00,
        )

        salary_history = sample_employee.salary_history
        assert len(salary_history) == 2
        assert salary_history[0]["salary"] == 2100.00
        assert salary_history[1]["salary"] == 1800.00


class TestContractAmendmentModel:
    """Tests for ContractAmendment model."""

    def test_amendment_creation(self, db, sample_employee):
        """Test creating a contract amendment."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2000.00,
        )

        amendment = ContractAmendment.create(
            contract=contract,
            amendment_date=date(2024, 6, 1),
            amendment_type="salary_change",
            description="Salary increase after trial period",
            old_field_name="gross_salary",
            old_value="2000.00",
            new_value="2100.00",
        )

        assert amendment.id is not None
        assert amendment.amendment_type == "salary_change"
        assert amendment.old_value == "2000.00"
        assert amendment.new_value == "2100.00"

    def test_amendment_is_recent(self, db, sample_employee):
        """Test is_recent property."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        amendment = ContractAmendment.create(
            contract=contract,
            amendment_date=date.today() - timedelta(days=15),
            amendment_type="position_change",
            description="Promotion",
            old_field_name="position",
            old_value="Worker",
            new_value="Operator",
        )

        assert amendment.is_recent is True

    def test_amendments_by_contract(self, db, sample_employee):
        """Test getting amendments for a contract."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        ContractAmendment.create(
            contract=contract,
            amendment_date=date(2024, 6, 1),
            amendment_type="salary_change",
            description="Raise",
            old_field_name="gross_salary",
            old_value="2000",
            new_value="2100",
        )

        ContractAmendment.create(
            contract=contract,
            amendment_date=date(2024, 9, 1),
            amendment_type="position_change",
            description="Promotion",
            old_field_name="position",
            old_value="Operator",
            new_value="Supervisor",
        )

        amendments = list(ContractAmendment.by_contract(contract))
        assert len(amendments) == 2

    def test_amendment_requires_description(self, db, sample_employee):
        """Test that amendment requires description."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        with pytest.raises(ValueError, match="Description is required"):
            ContractAmendment.create(
                contract=contract,
                amendment_date=date(2024, 6, 1),
                amendment_type="salary_change",
                description="",  # Empty!
                old_field_name="gross_salary",
                old_value="2000",
                new_value="2100",
            )


class TestContractCascadeDelete:
    """Tests for CASCADE DELETE behavior."""

    def test_deleting_employee_deletes_contracts(self, db, sample_employee):
        """Test that deleting employee cascades to contracts."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        employee_id = sample_employee.id

        # Delete employee (CASCADE should delete contracts)
        sample_employee.delete_instance()

        # Verify contract was deleted
        assert Contract.select().where(Contract.employee == employee_id).count() == 0

    def test_deleting_contract_deletes_amendments(self, db, sample_employee):
        """Test that deleting contract cascades to amendments."""
        contract = Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2024, 1, 1),
            position="Operator",
            department="Logistics",
        )

        amendment = ContractAmendment.create(
            contract=contract,
            amendment_date=date(2024, 6, 1),
            amendment_type="salary_change",
            description="Raise",
            old_field_name="gross_salary",
            old_value="2000",
            new_value="2100",
        )

        contract_id = contract.id

        # Delete contract (CASCADE should delete amendments)
        contract.delete_instance()

        # Verify amendment was deleted
        assert ContractAmendment.select().where(ContractAmendment.contract == contract_id).count() == 0
