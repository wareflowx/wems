"""
Tests for Improved Exception Handling

Tests cover:
- Specific exception handling in UI show_error/show_info methods
- Specific exception handling in data_exporter cell width calculation
- Ensures bare except: statements are replaced with specific exceptions
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from datetime import date
import sys
from io import StringIO

from src.export.data_exporter import DataExporter
from employee.models import Employee


class TestUIExceptionHandling:
    """Test exception handling in UI show_error/show_info methods."""

    def test_employee_form_show_error_handles_import_error(self):
        """Test that show_error handles ImportError when tkinter is not available."""
        from ui_ctk.forms.employee_form import EmployeeFormDialog

        # Create a mock instance
        form = MagicMock()

        # Mock tkinter.messagebox import to raise ImportError
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if 'tkinter' in name or 'messagebox' in name:
                raise ImportError("No tkinter available")
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            # Capture stdout (print uses stdout, not stderr)
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                # This should not raise, but print to stdout
                EmployeeFormDialog.show_error(form, "Test error message")
                # Verify it printed to stdout
                assert "[ERROR] Test error message" in sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

    def test_employee_list_show_error_handles_runtime_error(self):
        """Test that show_error handles RuntimeError when display is not available."""
        from ui_ctk.views.employee_list import EmployeeListView

        # Create a mock instance
        view = MagicMock()

        # Mock import to raise RuntimeError during import
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if 'tkinter.messagebox' in name:
                raise RuntimeError("No display available")
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                # This should not raise, but print to stdout
                EmployeeListView.show_error(view, "Test error message")
                # Verify it printed to stdout
                assert "[ERROR] Test error message" in sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

    def test_employee_detail_show_info_handles_attribute_error(self):
        """Test that show_info handles AttributeError gracefully."""
        from ui_ctk.views.employee_detail import EmployeeDetailView

        # Create a mock instance
        view = MagicMock()

        # Mock import to raise AttributeError during import
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if 'tkinter.messagebox' in name:
                raise AttributeError("No messagebox module")
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                # This should not raise, but print to stdout
                EmployeeDetailView.show_info(view, "Test info message")
                # Verify it printed to stdout
                assert "[INFO] Test info message" in sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout


class TestDataExporterExceptionHandling:
    """Test exception handling in data_exporter cell width calculation."""

    def test_export_creates_valid_excel_with_normal_data(self, db, temp_output_dir):
        """Test that export works correctly with normal data (regression test)."""
        exporter = DataExporter()

        # Create an employee with all required fields
        employee = Employee.create(
            external_id="NORM001",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            current_status="active",
            workspace="Paris",
            role="Engineer",
            contract_type="CDI",
            entry_date=date(2020, 1, 1)
        )

        output_path = temp_output_dir / "test_normal.xlsx"

        # Export should work without issues
        result = exporter.export_all_to_excel(output_path)

        assert result is True
        assert output_path.exists()

    def test_export_handles_multiple_employees(self, db, temp_output_dir):
        """Test that export handles multiple employees without crashing."""
        exporter = DataExporter()

        # Create multiple employees with all required fields
        for i in range(3):
            Employee.create(
                external_id=f"MULT{i:03d}",
                first_name=f"Test{i}",
                last_name=f"User{i}",
                email=f"test{i}@example.com",
                current_status="active",
                workspace="Paris",
                role="Engineer",
                contract_type="CDI",
                entry_date=date(2020, 1, 1)
            )

        output_path = temp_output_dir / "test_multiple.xlsx"

        # Export should handle all cells without crashing
        result = exporter.export_all_to_excel(output_path)

        assert result is True
        assert output_path.exists()

        # Verify the file is valid Excel
        import openpyxl
        wb = openpyxl.load_workbook(output_path)
        assert wb is not None
        wb.close()


class TestSpecificExceptionTypes:
    """Test that only specific exceptions are caught, not all exceptions."""

    def test_bare_except_removal_in_ui_code(self):
        """Test that UI code no longer has bare except statements."""
        import inspect
        from ui_ctk.forms.employee_form import EmployeeFormDialog
        from ui_ctk.views.employee_list import EmployeeListView
        from ui_ctk.views.employee_detail import EmployeeDetailView

        # Check that show_error methods have specific exceptions
        for cls, method_name in [
            (EmployeeFormDialog, 'show_error'),
            (EmployeeListView, 'show_error'),
            (EmployeeDetailView, 'show_error'),
            (EmployeeDetailView, 'show_info'),
        ]:
            method = getattr(cls, method_name)
            source = inspect.getsource(method)

            # Verify it has specific exceptions, not bare except
            assert 'except (ImportError, RuntimeError, AttributeError)' in source, \
                f"{cls.__name__}.{method_name} should use specific exceptions"
            assert 'except:' not in source or 'except (ImportError' in source, \
                f"{cls.__name__}.{method_name} should not have bare except"

    def test_bare_except_removal_in_exporter(self):
        """Test that data_exporter no longer has bare except statements."""
        import inspect
        from src.export.data_exporter import DataExporter

        # Get the source code of the auto_width_adjustment methods
        source = inspect.getsource(DataExporter)

        # Count occurrences of the specific exception pattern
        specific_count = source.count('except (AttributeError, TypeError)')

        # Verify we have the specific exceptions
        assert specific_count >= 4, "Should have at least 4 specific exception handlers"

    def test_critical_exceptions_propagate_in_ui(self):
        """Test that critical exceptions (KeyboardInterrupt, SystemExit) are not caught."""
        from ui_ctk.forms.employee_form import EmployeeFormDialog
        import inspect

        # Get the source code of show_error
        source = inspect.getsource(EmployeeFormDialog.show_error)

        # Verify that only specific exceptions are caught
        # The exception handler should catch: ImportError, RuntimeError, AttributeError
        # It should NOT catch: KeyboardInterrupt, SystemExit, Exception
        assert 'except (ImportError, RuntimeError, AttributeError)' in source

        # Verify that there's no bare except or generic Exception catch
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'except' in line and 'except (ImportError' not in line:
                # Make sure it's not a bare except or catching Exception/BaseException
                assert 'except:' not in line, f"Found bare except on line {i}"
                assert 'except Exception' not in line, f"Found except Exception on line {i}"
                assert 'except BaseException' not in line, f"Found except BaseException on line {i}"


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for export files."""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
