"""Integration tests for validators with models."""

import pytest
from datetime import date

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from employee.validators import (
    ValidationError,
    validate_external_id,
    validate_entry_date,
    validate_caces_kind,
    validate_medical_visit_consistency,
)


# =============================================================================
# INTEGRATION TESTS: Employee with Validators
# =============================================================================

class TestEmployeeValidationIntegration:
    """Integration tests for Employee model validation."""

    def test_create_employee_with_valid_data(self, db):
        """Should create employee with valid data."""
        employee = Employee.create(
            external_id="WMS-001",
            first_name="John",
            last_name="Doe",
            current_status="active",
            workspace="Quai",
            role="Cariste",
            contract_type="CDI",
            entry_date=date(2020, 1, 15)
        )

        assert employee.id is not None
        assert employee.external_id == "WMS-001"
        assert employee.entry_date == date(2020, 1, 15)

    def test_create_employee_with_invalid_id_path_traversal(self, db):
        """Should reject employee with path traversal in ID."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            Employee.create(
                external_id="../etc/passwd",
                first_name="John",
                last_name="Doe",
                current_status="active",
                workspace="Quai",
                role="Cariste",
                contract_type="CDI",
                entry_date=date(2020, 1, 15)
            )

        # Error should be about validation/path traversal
        assert "external_id" in str(exc.value).lower() or "path" in str(exc.value).lower()

    def test_create_employee_with_invalid_id_format(self, db):
        """Should reject employee with invalid ID format."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            Employee.create(
                external_id="ID WITH SPACES",
                first_name="John",
                last_name="Doe",
                current_status="active",
                workspace="Quai",
                role="Cariste",
                contract_type="CDI",
                entry_date=date(2020, 1, 15)
            )

        # Should mention the validation issue
        error_str = str(exc.value).lower()
        assert "external_id" in error_str or "invalid" in error_str

    def test_create_employee_with_future_entry_date(self, db):
        """Should reject employee with future entry date."""
        future_date = date(2100, 1, 1)

        with pytest.raises((ValidationError, ValueError)) as exc:
            Employee.create(
                external_id="WMS-001",
                first_name="John",
                last_name="Doe",
                current_status="active",
                workspace="Quai",
                role="Cariste",
                contract_type="CDI",
                entry_date=future_date
            )

        # Should mention the date validation issue
        error_str = str(exc.value).lower()
        assert "entry_date" in error_str or "future" in error_str

    def test_create_employee_with_too_old_entry_date(self, db):
        """Should reject employee with entry date before 1900."""
        old_date = date(1800, 1, 1)

        with pytest.raises((ValidationError, ValueError)) as exc:
            Employee.create(
                external_id="WMS-001",
                first_name="John",
                last_name="Doe",
                current_status="active",
                workspace="Quai",
                role="Cariste",
                contract_type="CDI",
                entry_date=old_date
            )

        # Should mention the date validation issue
        error_str = str(exc.value).lower()
        assert "entry_date" in error_str or "old" in error_str


# =============================================================================
# INTEGRATION TESTS: CACES with Validators
# =============================================================================

class TestCacesValidationIntegration:
    """Integration tests for CACES model validation."""

    def test_create_caces_with_valid_kind(self, db, sample_employee):
        """Should create CACES with valid kind."""
        caces = Caces.create(
            employee=sample_employee,
            kind="R489-1A",
            completion_date=date(2020, 3, 1)
        )

        assert caces.id is not None
        assert caces.kind == "R489-1A"

    def test_create_caces_with_invalid_kind(self, db, sample_employee):
        """Should reject CACES with invalid kind."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            Caces.create(
                employee=sample_employee,
                kind="R489-2",  # Invalid type
                completion_date=date(2020, 3, 1)
            )

        # Should mention the kind validation issue
        error_str = str(exc.value).lower()
        assert "kind" in error_str or "type" in error_str or "invalid" in error_str

    def test_create_caces_with_lowercase_kind(self, db, sample_employee):
        """Should accept lowercase kind and convert to uppercase."""
        caces = Caces.create(
            employee=sample_employee,
            kind="r489-1b",  # Lowercase input
            completion_date=date(2020, 3, 1)
        )

        assert caces.kind == "R489-1B"  # Should be uppercase


# =============================================================================
# INTEGRATION TESTS: MedicalVisit with Validators
# =============================================================================

class TestMedicalVisitValidationIntegration:
    """Integration tests for MedicalVisit model validation."""

    def test_create_visit_initial_fit(self, db, sample_employee):
        """Should create initial visit with fit result."""
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type="initial",
            visit_date=date(2024, 1, 15),
            result="fit"
        )

        assert visit.id is not None
        assert visit.visit_type == "initial"
        assert visit.result == "fit"

    def test_create_visit_periodic_unfit(self, db, sample_employee):
        """Should create periodic visit with unfit result."""
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type="periodic",
            visit_date=date(2024, 1, 15),
            result="unfit"
        )

        assert visit.id is not None
        assert visit.result == "unfit"

    def test_create_visit_recovery_with_restrictions(self, db, sample_employee):
        """Should create recovery visit with restrictions."""
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type="recovery",
            visit_date=date(2024, 1, 15),
            result="fit_with_restrictions"
        )

        assert visit.id is not None
        assert visit.visit_type == "recovery"
        assert visit.result == "fit_with_restrictions"

    def test_create_visit_recovery_without_restrictions_fit(self, db, sample_employee):
        """Should reject recovery visit with fit result."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            MedicalVisit.create(
                employee=sample_employee,
                visit_type="recovery",
                visit_date=date(2024, 1, 15),
                result="fit"
            )

        # Should mention the consistency issue
        error_str = str(exc.value).lower()
        assert "restrictions" in error_str or "recovery" in error_str

    def test_create_visit_recovery_without_restrictions_unfit(self, db, sample_employee):
        """Should reject recovery visit with unfit result."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            MedicalVisit.create(
                employee=sample_employee,
                visit_type="recovery",
                visit_date=date(2024, 1, 15),
                result="unfit"
            )

        # Should mention the consistency issue
        error_str = str(exc.value).lower()
        assert "restrictions" in error_str or "recovery" in error_str

    def test_create_visit_invalid_type(self, db, sample_employee):
        """Should reject visit with invalid type."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            MedicalVisit.create(
                employee=sample_employee,
                visit_type="invalid_type",
                visit_date=date(2024, 1, 15),
                result="fit"
            )

        # Should mention invalid visit type
        error_str = str(exc.value).lower()
        assert "visit_type" in error_str or "invalid" in error_str

    def test_create_visit_invalid_result(self, db, sample_employee):
        """Should reject visit with invalid result."""
        with pytest.raises((ValidationError, ValueError)) as exc:
            MedicalVisit.create(
                employee=sample_employee,
                visit_type="initial",
                visit_date=date(2024, 1, 15),
                result="invalid_result"
            )

        # Should mention invalid result
        error_str = str(exc.value).lower()
        assert "result" in error_str or "invalid" in error_str


# =============================================================================
# INTEGRATION TESTS: OnlineTraining with Validators
# =============================================================================

class TestOnlineTrainingValidationIntegration:
    """Integration tests for OnlineTraining model validation."""

    def test_create_training_with_validity(self, db, sample_employee):
        """Should create training with validity period."""
        training = OnlineTraining.create(
            employee=sample_employee,
            title="Safety Training",
            completion_date=date(2024, 1, 15),
            validity_months=12
        )

        assert training.id is not None
        assert training.validity_months == 12
        assert training.expiration_date is not None

    def test_create_training_permanent(self, db, sample_employee):
        """Should create permanent training."""
        training = OnlineTraining.create(
            employee=sample_employee,
            title="Fire Safety",
            completion_date=date(2024, 1, 15),
            validity_months=None
        )

        assert training.id is not None
        assert training.validity_months is None
        assert training.expiration_date is None


# =============================================================================
# INTEGRATION TESTS: Multiple Validators
# =============================================================================

class TestMultipleValidatorsIntegration:
    """Tests for multiple validators working together."""

    def test_employee_full_validation_pipeline(self, db):
        """Test complete validation pipeline for employee creation."""
        # This should succeed
        employee = Employee.create(
            external_id="VALID-ID-123",
            first_name="Test",
            last_name="User",
            current_status="active",
            workspace="Quai",
            role="Cariste",
            contract_type="CDI",
            entry_date=date(2020, 1, 15)
        )

        assert employee.id is not None

        # Add CACES with validation
        caces = Caces.create(
            employee=employee,
            kind="R489-1A",
            completion_date=date(2020, 3, 1)
        )

        assert caces.id is not None

        # Add medical visit with validation
        visit = MedicalVisit.create(
            employee=employee,
            visit_type="initial",
            visit_date=date(2020, 1, 20),
            result="fit"
        )

        assert visit.id is not None

    def test_employee_validation_failures_cascade(self, db):
        """Test that validation failures prevent database corruption."""
        initial_count = Employee.select().count()

        # Try to create employee with invalid data
        try:
            Employee.create(
                external_id="INVALID ID WITH SPACES",
                first_name="Test",
                last_name="User",
                current_status="active",
                workspace="Quai",
                role="Cariste",
                contract_type="CDI",
                entry_date=date(2020, 1, 15)
            )
            # Should not reach here
            assert False, "Should have raised ValidationError"
        except (ValidationError, ValueError):
            # Expected
            pass

        # Verify no employee was created
        final_count = Employee.select().count()
        assert final_count == initial_count, "Database should not be corrupted by validation failure"

    def test_update_employee_with_valid_data(self, db, sample_employee):
        """Should allow updating employee with valid data."""
        # Update with valid external_id (should not conflict with itself)
        sample_employee.external_id = "UPDATED-ID"
        sample_employee.save()

        # Reload from database
        updated = Employee.get_by_id(sample_employee.id)
        assert updated.external_id == "UPDATED-ID"

    def test_update_preserves_validation(self, db, sample_employee):
        """Should validate on update, not just create."""
        # Try to set invalid external_id
        with pytest.raises((ValidationError, ValueError)):
            sample_employee.external_id = "../invalid/path"
            sample_employee.save()

        # Reload and verify the value didn't change
        reloaded = Employee.get_by_id(sample_employee.id)
        assert reloaded.external_id != "../invalid/path"
