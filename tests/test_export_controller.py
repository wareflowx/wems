"""Tests for export controller."""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from controllers.export_controller import ExportController
from employee.models import Employee


@pytest.fixture
def export_controller():
    """Create an export controller instance."""
    return ExportController()


@pytest.fixture
def sample_employees(db):
    """Create sample employees for testing."""
    employees = []
    for i in range(3):
        emp = Employee.create(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}@example.com",
            phone="1234567890",
            workspace="Warehouse A",
            role="Operator",
            contract_type="CDI",
            current_status="active",
            entry_date=date.today(),
        )
        employees.append(emp)
    return employees


class TestExportController:
    """Test suite for ExportController."""

    def test_initialization(self, export_controller):
        """Test controller initialization."""
        assert export_controller._export_thread is None
        assert export_controller._is_exporting is False

    def test_is_exporting_initially_false(self, export_controller):
        """Test that is_exporting returns False initially."""
        assert export_controller.is_exporting() is False

    def test_export_employees_starts_thread(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test that export_employees starts a background thread."""
        output_file = tmp_path / "test_export.xlsx"

        # Mock callbacks
        progress_callback = MagicMock()
        completion_callback = MagicMock()

        # Start export
        result = export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
        )

        # Verify export started
        assert result is True
        assert export_controller.is_exporting()

        # Wait for export to complete
        import time

        time.sleep(2)

        # Verify callbacks were called
        assert progress_callback.called
        assert completion_callback.called

    def test_export_employees_creates_file(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test that export creates an Excel file."""
        output_file = tmp_path / "test_export.xlsx"

        # Start export and wait for completion
        export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            progress_callback=None,
            completion_callback=None,
        )

        # Wait for export to complete
        import time

        time.sleep(2)

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_export_employees_with_all_sheets(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test export with all sheets enabled."""
        output_file = tmp_path / "test_all_sheets.xlsx"

        # Start export with all sheets
        export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            include_caces=True,
            include_visits=True,
            include_trainings=True,
            progress_callback=None,
            completion_callback=None,
        )

        # Wait for completion
        import time

        time.sleep(2)

        # Verify file was created
        assert output_file.exists()

    def test_export_employees_without_optional_sheets(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test export without optional sheets."""
        output_file = tmp_path / "test_minimal.xlsx"

        # Start export without optional sheets
        export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            include_caces=False,
            include_visits=False,
            include_trainings=False,
            progress_callback=None,
            completion_callback=None,
        )

        # Wait for completion
        import time

        time.sleep(2)

        # Verify file was created
        assert output_file.exists()

    def test_export_while_exporting_returns_false(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test that starting an export while one is in progress returns False."""
        output_file1 = tmp_path / "test1.xlsx"
        output_file2 = tmp_path / "test2.xlsx"

        completion_callback = MagicMock()

        # Start first export
        result1 = export_controller.export_employees(
            output_path=output_file1,
            employees=sample_employees,
            completion_callback=completion_callback,
        )

        # Try to start second export immediately
        result2 = export_controller.export_employees(
            output_path=output_file2,
            employees=sample_employees,
            completion_callback=completion_callback,
        )

        # First should succeed, second should fail
        assert result1 is True
        assert result2 is False

        # Verify completion callback was called with error for second attempt
        completion_callback.assert_called_with(False, "An export is already in progress")

    def test_cancel_export_when_not_exporting(self, export_controller):
        """Test cancel_export when no export is in progress."""
        result = export_controller.cancel_export()
        assert result is False

    def test_progress_callback_receives_correct_values(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test that progress callback receives expected values."""
        output_file = tmp_path / "test_progress.xlsx"

        progress_calls = []

        def track_progress(message, percentage):
            progress_calls.append((message, percentage))

        export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            progress_callback=track_progress,
            completion_callback=None,
        )

        # Wait for completion
        import time

        time.sleep(2)

        # Verify progress was tracked
        assert len(progress_calls) > 0

        # Check final call has 100%
        final_message, final_percentage = progress_calls[-1]
        assert final_percentage == 100

    def test_completion_callback_success(
        self, export_controller, sample_employees, tmp_path
    ):
        """Test completion callback on successful export."""
        output_file = tmp_path / "test_success.xlsx"

        completion_calls = []

        def track_completion(success, message):
            completion_calls.append((success, message))

        export_controller.export_employees(
            output_path=output_file,
            employees=sample_employees,
            completion_callback=track_completion,
        )

        # Wait for completion
        import time

        time.sleep(2)

        # Verify completion was called
        assert len(completion_calls) > 0

        # Check success
        success, message = completion_calls[-1]
        assert success is True
        assert str(output_file) in message

    def test_empty_employee_list(
        self, export_controller, tmp_path
    ):
        """Test export with empty employee list."""
        output_file = tmp_path / "test_empty.xlsx"

        # Export empty list
        export_controller.export_employees(
            output_path=output_file,
            employees=[],
            progress_callback=None,
            completion_callback=None,
        )

        # Wait for completion
        import time

        time.sleep(2)

        # File should still be created (with summary sheet)
        assert output_file.exists()
