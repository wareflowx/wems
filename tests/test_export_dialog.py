"""Tests for export dialog components."""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from employee.models import Employee
from ui_ctk.widgets.export_button import ExportButton


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


class TestExportButton:
    """Test suite for ExportButton widget."""

    def test_initialization(self, sample_employees):
        """Test ExportButton initialization."""
        # Create mock parent widget
        parent = MagicMock()

        # Create get_employees function
        def get_employees():
            return sample_employees

        # Mock the widget creation (skip actual GUI)
        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", return_value=None):
            button = ExportButton(
                parent,
                get_employees_func=get_employees,
                title="Test Export",
                default_filename="test.xlsx",
            )

            # Verify attributes
            assert button.get_employees_func == get_employees
            assert button.title == "Test Export"
            assert button.default_filename == "test.xlsx"
            assert button.on_export_complete is None

    def test_initialization_with_completion_callback(self, sample_employees):
        """Test ExportButton with completion callback."""
        parent = MagicMock()

        def get_employees():
            return sample_employees

        completion_callback = MagicMock()

        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", return_value=None):
            button = ExportButton(
                parent,
                get_employees_func=get_employees,
                on_export_complete=completion_callback,
            )

            assert button.on_export_complete == completion_callback

    def test_get_employees_func_returns_employees(self, sample_employees):
        """Test that get_employees_func returns correct employees."""
        parent = MagicMock()

        def get_employees():
            return sample_employees

        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", return_value=None):
            button = ExportButton(
                parent,
                get_employees_func=get_employees,
            )

            result = button.get_employees_func()
            assert len(result) == 3
            assert all(isinstance(emp, Employee) for emp in result)

    def test_custom_button_properties(self, sample_employees):
        """Test custom button properties can be set."""
        parent = MagicMock()

        def get_employees():
            return sample_employees

        # Mock the super().__init__ to capture kwargs
        init_kwargs = {}

        def mock_init(self, master, **kwargs):
            init_kwargs.update(kwargs)

        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", mock_init):
            button = ExportButton(
                parent,
                get_employees_func=get_employees,
                text="Custom Export",
                width=200,
                fg_color="#FF0000",
            )

            # Verify custom kwargs were passed through
            assert init_kwargs["text"] == "Custom Export"
            assert init_kwargs["width"] == 200
            assert init_kwargs["fg_color"] == "#FF0000"


class TestExportButtonIntegration:
    """Integration tests for ExportButton with ExportController."""

    def test_export_button_with_empty_list(self, db):
        """Test ExportButton behavior with empty employee list."""
        parent = MagicMock()

        def get_employees():
            return []

        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", return_value=None):
            button = ExportButton(
                parent,
                get_employees_func=get_employees,
            )

            # Should return empty list
            result = button.get_employees_func()
            assert len(result) == 0

    def test_export_button_filters_employees(self, db):
        """Test ExportButton with filtered employee list."""
        parent = MagicMock()

        # Create employees with different statuses
        active_emp = Employee.create(
            first_name="Active",
            last_name="Employee",
            email="active@example.com",
            current_status="active",
            entry_date=date.today(),
            workspace="Warehouse A",
            role="Operator",
            contract_type="CDI",
        )
        inactive_emp = Employee.create(
            first_name="Inactive",
            last_name="Employee",
            email="inactive@example.com",
            current_status="inactive",
            entry_date=date.today(),
            workspace="Warehouse A",
            role="Operator",
            contract_type="CDI",
        )

        # Return only active employees
        def get_active_employees():
            return [active_emp]

        with patch("ui_ctk.widgets.export_button.ctk.CTkButton.__init__", return_value=None):
            button = ExportButton(
                parent,
                get_employees_func=get_active_employees,
            )

            result = button.get_employees_func()
            assert len(result) == 1
            assert result[0].id == active_emp.id
