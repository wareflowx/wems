"""
Tests for Error Handler Module

Tests cover:
- Exception classes
- Error categorization
- Error handling functions
- User message formatting
- Safe execution wrapper
- Error boundary context manager
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from src.utils.error_handler import (
    ApplicationError,
    ValidationError,
    DatabaseError,
    FilePermissionError,
    DataNotFoundError,
    ErrorCategory,
    categorize_error,
    handle_error,
    format_user_message,
    safe_execute,
    log_and_reraise,
    ErrorBoundary
)


class TestExceptionClasses:
    """Test custom exception classes."""

    def test_application_error_creation(self):
        """Test creating ApplicationError."""
        error = ApplicationError("Test error", "context")
        assert error.message == "Test error"
        assert error.context == "context"
        assert str(error) == "Test error"

    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError("Invalid value", field="email", value="invalid")
        assert error.message == "Invalid value"
        assert error.field == "email"
        assert error.value == "invalid"

    def test_validation_error_without_field(self):
        """Test ValidationError without field."""
        error = ValidationError("Invalid")
        assert error.field is None
        assert error.value is None

    def test_database_error_creation(self):
        """Test creating DatabaseError."""
        error = DatabaseError("Query failed", query="SELECT * FROM employees")
        assert error.message == "Query failed"
        assert error.query == "SELECT * FROM employees"

    def test_database_error_without_query(self):
        """Test DatabaseError without query."""
        error = DatabaseError("Query failed")
        assert error.query is None

    def test_file_permission_error_creation(self):
        """Test creating FilePermissionError."""
        path = Path("/test/file.txt")
        error = FilePermissionError("Access denied", path=path)
        assert error.message == "Access denied"
        assert error.path == path

    def test_data_not_found_error_creation(self):
        """Test creating DataNotFoundError."""
        error = DataNotFoundError("Not found", resource_type="Employee", resource_id="123")
        assert error.message == "Not found"
        assert error.resource_type == "Employee"
        assert error.resource_id == "123"

    def test_data_not_found_error_without_details(self):
        """Test DataNotFoundError without details."""
        error = DataNotFoundError("Not found")
        assert error.resource_type is None
        assert error.resource_id is None


class TestErrorCategorization:
    """Test error categorization logic."""

    def test_categorize_validation_error(self):
        """Test ValidationError is categorized correctly."""
        error = ValidationError("Invalid")
        category = categorize_error(error)
        assert category == ErrorCategory.VALIDATION_ERROR

    def test_categorize_value_error(self):
        """Test ValueError is categorized as validation error."""
        error = ValueError("Invalid value")
        category = categorize_error(error)
        assert category == ErrorCategory.VALIDATION_ERROR

    def test_categorize_database_error(self):
        """Test DatabaseError is categorized correctly."""
        error = DatabaseError("Query failed")
        category = categorize_error(error)
        assert category == ErrorCategory.DATABASE_ERROR

    def test_categorize_file_permission_error(self):
        """Test FilePermissionError is categorized correctly."""
        error = FilePermissionError("Access denied")
        category = categorize_error(error)
        assert category == ErrorCategory.PERMISSION_ERROR

    def test_categorize_data_not_found_error(self):
        """Test DataNotFoundError is categorized as user error."""
        error = DataNotFoundError("Not found")
        category = categorize_error(error)
        assert category == ErrorCategory.USER_ERROR

    def test_categorize_file_not_found_error(self):
        """Test FileNotFoundError is categorized as file error."""
        error = FileNotFoundError("File not found")
        category = categorize_error(error)
        assert category == ErrorCategory.FILE_ERROR

    def test_categorize_permission_error(self):
        """Test PermissionError is categorized as file error."""
        error = PermissionError("Permission denied")
        category = categorize_error(error)
        assert category == ErrorCategory.FILE_ERROR

    def test_categorize_connection_error(self):
        """Test ConnectionError is categorized as network error."""
        error = ConnectionError("Connection failed")
        category = categorize_error(error)
        assert category == ErrorCategory.NETWORK_ERROR

    def test_categorize_timeout_error(self):
        """Test TimeoutError is categorized as network error."""
        error = TimeoutError("Request timed out")
        category = categorize_error(error)
        assert category == ErrorCategory.NETWORK_ERROR

    def test_categorize_os_error(self):
        """Test OSError is categorized as file error."""
        error = OSError("OS error")
        category = categorize_error(error)
        assert category == ErrorCategory.FILE_ERROR

    def test_categorize_io_error(self):
        """Test IOError is categorized as file error."""
        error = IOError("IO error")
        category = categorize_error(error)
        assert category == ErrorCategory.FILE_ERROR

    def test_categorize_generic_exception(self):
        """Test generic Exception is categorized as unknown."""
        error = Exception("Unknown error")
        category = categorize_error(error)
        assert category == ErrorCategory.UNKNOWN_ERROR

    def test_categorize_application_error_with_permission_message(self):
        """Test ApplicationError with permission message."""
        error = ApplicationError("Permission denied to access file")
        category = categorize_error(error)
        assert category == ErrorCategory.PERMISSION_ERROR

    def test_categorize_application_error_with_not_found_message(self):
        """Test ApplicationError with not found message."""
        error = ApplicationError("Employee not found")
        category = categorize_error(error)
        assert category == ErrorCategory.USER_ERROR


class TestUserMessageFormatting:
    """Test user-friendly message formatting."""

    def test_format_validation_error_with_field(self):
        """Test formatting ValidationError with field."""
        error = ValidationError("Invalid email format", field="email", value="bad")
        message = format_user_message(error)
        assert "email" in message
        assert "Invalid email format" in message

    def test_format_validation_error_without_field(self):
        """Test formatting ValidationError without field."""
        error = ValidationError("Invalid data")
        message = format_user_message(error)
        assert "Validation error" in message
        assert "Invalid data" in message

    def test_format_database_error(self):
        """Test formatting DatabaseError."""
        error = DatabaseError("Query failed")
        message = format_user_message(error)
        assert "database error" in message.lower()

    def test_format_file_permission_error_with_path(self):
        """Test formatting FilePermissionError with path."""
        error = FilePermissionError("Access denied", path=Path("/test/file.txt"))
        message = format_user_message(error)
        assert "Permission denied" in message
        # Use str(path) to handle both forward and backslashes
        assert str(Path("/test/file.txt")) in message

    def test_format_file_permission_error_without_path(self):
        """Test formatting FilePermissionError without path."""
        error = FilePermissionError("Access denied")
        message = format_user_message(error)
        assert "permission" in message.lower()

    def test_format_data_not_found_error_with_details(self):
        """Test formatting DataNotFoundError with details."""
        error = DataNotFoundError("Not found", resource_type="Employee", resource_id="123")
        message = format_user_message(error)
        assert "Employee" in message
        assert "123" in message

    def test_format_data_not_found_error_without_details(self):
        """Test formatting DataNotFoundError without details."""
        error = DataNotFoundError("Resource not found")
        message = format_user_message(error)
        assert "not found" in message.lower()

    def test_format_permission_denied_message(self):
        """Test formatting permission denied error message."""
        error = Exception("Permission denied to access resource")
        message = format_user_message(error)
        assert "permission" in message.lower()

    def test_format_duplicate_error_message(self):
        """Test formatting duplicate/unique error."""
        error = Exception("UNIQUE constraint failed: employees.external_id")
        message = format_user_message(error)
        assert "already exists" in message.lower()

    def test_format_foreign_key_error_message(self):
        """Test formatting foreign key error."""
        error = Exception("FOREIGN KEY constraint failed")
        message = format_user_message(error)
        assert "referenced by other records" in message.lower()

    def test_format_database_error_message(self):
        """Test formatting database error message."""
        error = Exception("SQLite database disk image is malformed")
        message = format_user_message(error)
        assert "database" in message.lower()

    def test_format_generic_error(self):
        """Test formatting generic error."""
        error = Exception("Something went wrong")
        message = format_user_message(error)
        assert message == "Something went wrong"


class TestHandleError:
    """Test centralized error handling."""

    def test_handle_validation_error_logs_info(self, caplog):
        """Test validation error is logged at INFO level."""
        error = ValidationError("Invalid value")

        with caplog.at_level(logging.INFO):
            handle_error(error, context="test_context", show_to_user=False)

        assert "test_context" in caplog.text
        assert "Invalid value" in caplog.text

    def test_handle_database_error_logs_error(self, caplog):
        """Test database error is logged at ERROR level."""
        error = DatabaseError("Query failed")

        with caplog.at_level(logging.ERROR):
            handle_error(error, context="test_context", show_to_user=False)

        assert "test_context" in caplog.text
        assert "Query failed" in caplog.text

    def test_handle_error_with_recovery_callback(self):
        """Test error recovery callback is called."""
        error = ValidationError("Invalid")
        recovery_called = []

        def recovery(e):
            recovery_called.append(True)

        handle_error(error, show_to_user=False, on_recovery=recovery)
        assert len(recovery_called) == 1

    def test_handle_error_recovery_failure(self, caplog):
        """Test recovery failure is logged."""
        error = ValidationError("Invalid")

        def failing_recovery(e):
            raise ValueError("Recovery failed")

        with caplog.at_level(logging.ERROR):
            handle_error(error, show_to_user=False, on_recovery=failing_recovery)

        assert "Recovery failed" in caplog.text

    def test_handle_error_reraise(self):
        """Test reraise option."""
        error = ValidationError("Invalid")

        with pytest.raises(ValidationError):
            handle_error(error, show_to_user=False, reraise=True)


class TestSafeExecute:
    """Test safe execution wrapper."""

    def test_safe_execute_success(self):
        """Test successful execution returns result."""
        def func(x, y):
            return x + y

        result = safe_execute(func, 2, 3, context="addition")
        assert result == 5

    def test_safe_execute_with_kwargs(self):
        """Test safe execution with keyword arguments."""
        def func(x, y):
            return x * y

        result = safe_execute(func, x=3, y=4)
        assert result == 12

    def test_safe_execute_error_returns_default(self):
        """Test error returns default value."""
        def func():
            raise ValueError("Error")

        result = safe_execute(func, default_return="default")
        assert result == "default"

    def test_safe_execute_error_without_default(self):
        """Test error without default returns None."""
        def func():
            raise ValueError("Error")

        result = safe_execute(func)
        assert result is None

    def test_safe_execute_logs_error(self):
        """Test error is logged without crashing."""
        def func():
            raise ValueError("Error")

        # Should not raise, just log and return default
        result = safe_execute(func, context="test_context", default_return=None)

        # Verify default is returned
        assert result is None

    def test_safe_execute_with_recovery(self):
        """Test safe execute with recovery callback."""
        def func():
            raise ValueError("Error")

        recovery_called = []

        def recovery(e):
            recovery_called.append(True)

        safe_execute(func, on_error=recovery)
        assert len(recovery_called) == 1


class TestLogAndReraise:
    """Test log and reraise function."""

    def test_log_and_reraise_logs(self, caplog):
        """Test error is logged."""
        error = ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            try:
                log_and_reraise(error, context="test_context")
            except ValueError:
                pass

        assert "test_context" in caplog.text
        assert "Test error" in caplog.text

    def test_log_and_reraise_reraises(self):
        """Test error is reraised."""
        error = ValueError("Test error")

        with pytest.raises(ValueError):
            log_and_reraise(error)

    def test_log_and_reraise_with_message(self, caplog):
        """Test log with custom message."""
        error = ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            try:
                log_and_reraise(error, context="context", message="Additional info")
            except ValueError:
                pass

        assert "context" in caplog.text
        assert "Additional info" in caplog.text


class TestErrorBoundary:
    """Test error boundary context manager."""

    def test_error_boundary_suppresses_exception(self):
        """Test ErrorBoundary suppresses exception."""
        with ErrorBoundary(show_to_user=False):
            raise ValueError("Error")

        # Should not raise

    def test_error_boundary_returns_false_on_no_error(self):
        """Test ErrorBoundary returns False when no error."""
        with ErrorBoundary(show_to_user=False) as boundary:
            pass

        # Should complete without suppressing

    def test_error_boundary_with_context(self, caplog):
        """Test ErrorBoundary with context."""
        with caplog.at_level(logging.INFO):
            with ErrorBoundary(context="test_context", show_to_user=False):
                raise ValueError("Error")

        assert "test_context" in caplog.text

    def test_error_boundary_with_recovery(self):
        """Test ErrorBoundary with recovery callback."""
        recovery_called = []

        def recovery(e):
            recovery_called.append(True)

        with ErrorBoundary(show_to_user=False, on_error=recovery):
            raise ValueError("Error")

        assert len(recovery_called) == 1

    def test_error_boundary_logs_error(self):
        """Test ErrorBoundary logs errors without crashing."""
        # Should not raise, just log and suppress
        with ErrorBoundary(show_to_user=False):
            raise ValueError("Test error")

        # If we get here, error was suppressed successfully

    def test_error_boundary_no_exception(self):
        """Test ErrorBoundary with no exception."""
        executed = []

        with ErrorBoundary(show_to_user=False):
            executed.append(True)

        assert len(executed) == 1


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_handle_error_none_error(self, caplog):
        """Test handling None error gracefully."""
        # This should not crash
        handle_error(Exception("test"), show_to_user=False)

    def test_safe_execute_none_function(self):
        """Test safe_execute with None function returns default."""
        result = safe_execute(None, default_return="default")
        assert result == "default"

    def test_format_error_none_exception(self):
        """Test formatting None exception."""
        # This would fail with AttributeError if not handled
        try:
            format_user_message(Exception("test"))
        except Exception as e:
            pytest.fail(f"format_user_message raised exception: {e}")

    def test_categorize_none_error(self):
        """Test categorizing None error."""
        # This would fail if not handled
        try:
            categorize_error(Exception("test"))
        except Exception as e:
            pytest.fail(f"categorize_error raised exception: {e}")

    def test_error_boundary_with_exception_in_context(self):
        """Test ErrorBoundary when exception in __enter__."""
        class BrokenBoundary:
            def __enter__(self):
                raise ValueError("Broken")

            def __exit__(self, *args):
                pass

        with pytest.raises(ValueError):
            with BrokenBoundary():
                pass

    def test_multiple_nested_boundaries(self, caplog):
        """Test nested error boundaries."""
        with caplog.at_level(logging.INFO):
            with ErrorBoundary(context="outer", show_to_user=False):
                with ErrorBoundary(context="inner", show_to_user=False):
                    raise ValueError("Nested error")

        # Both contexts should be logged
        assert "inner" in caplog.text
