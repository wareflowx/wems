"""Tests for security logging module."""

import pytest
from unittest.mock import patch, MagicMock

from utils.security_logger import (
    log_authentication,
    log_authorization,
    log_data_access,
    log_file_operation,
    require_permission,
    log_suspicious_activity,
    SecurityAuditLogger,
    EVENT_LOGIN,
    EVENT_LOGOUT,
    EVENT_FAILED_LOGIN,
    EVENT_PASSWORD_CHANGE,
    EVENT_ACCESS_GRANTED,
    EVENT_ACCESS_DENIED,
)


class TestLogAuthentication:
    """Tests for log_authentication function."""

    def test_log_successful_login(self, caplog):
        """Test logging successful login."""
        with caplog.at_level(logging.INFO):
            log_authentication(
                "login", "testuser", success=True, ip_address="192.168.1.1"
            )
            assert len(caplog.records) > 0
            assert any("login" in record.message for record in caplog.records)

    def test_log_failed_login(self, caplog):
        """Test logging failed login."""
        with caplog.at_level(logging.WARNING):
            log_authentication(
                "failed_login", "testuser", success=False, ip_address="192.168.1.1"
            )
            assert len(caplog.records) > 0
            # Should be logged as WARNING
            assert any(record.levelno == logging.WARNING for record in caplog.records)

    def test_log_logout(self, caplog):
        """Test logging logout."""
        with caplog.at_level(logging.INFO):
            log_authentication("logout", "testuser", success=True)
            assert len(caplog.records) > 0

    def test_log_authentication_with_details(self, caplog):
        """Test logging authentication with additional details."""
        with caplog.at_level(logging.INFO):
            log_authentication(
                "login",
                "testuser",
                success=True,
                ip_address="192.168.1.1",
                details="Login via mobile app",
            )
            assert len(caplog.records) > 0

    def test_log_authentication_with_user_agent(self, caplog):
        """Test logging authentication with user agent."""
        with caplog.at_level(logging.INFO):
            log_authentication(
                "login",
                "testuser",
                success=True,
                user_agent="Mozilla/5.0 Browser",
            )
            assert len(caplog.records) > 0


class TestLogAuthorization:
    """Tests for log_authorization function."""

    def test_log_access_granted(self, caplog):
        """Test logging granted access."""
        with caplog.at_level(logging.INFO):
            log_authorization("employee", "view", "user123", granted=True)
            assert len(caplog.records) > 0

    def test_log_access_denied(self, caplog):
        """Test logging denied access."""
        with caplog.at_level(logging.WARNING):
            log_authorization(
                "employee", "delete", "user123", granted=False, reason="Insufficient permissions"
            )
            assert len(caplog.records) > 0
            assert any(record.levelno == logging.WARNING for record in caplog.records)

    def test_log_authorization_without_reason(self, caplog):
        """Test logging authorization without reason."""
        with caplog.at_level(logging.INFO):
            log_authorization("caces", "view", "user123", granted=True)
            assert len(caplog.records) > 0


class TestLogDataAccess:
    """Tests for log_data_access function."""

    def test_log_data_view(self, caplog):
        """Test logging data view."""
        with caplog.at_level(logging.INFO):
            log_data_access("employee", "123", "view", "user456", success=True)
            assert len(caplog.records) > 0

    def test_log_data_create(self, caplog):
        """Test logging data creation."""
        with caplog.at_level(logging.INFO):
            log_data_access("employee", "456", "create", "admin", success=True)
            assert len(caplog.records) > 0

    def test_log_data_update(self, caplog):
        """Test logging data update."""
        with caplog.at_level(logging.INFO):
            log_data_access("employee", "789", "update", "manager", success=True)
            assert len(caplog.records) > 0

    def test_log_data_delete(self, caplog):
        """Test logging data deletion."""
        with caplog.at_level(logging.INFO):
            log_data_access("employee", "999", "delete", "admin", success=True)
            assert len(caplog.records) > 0

    def test_log_failed_data_access(self, caplog):
        """Test logging failed data access."""
        with caplog.at_level(logging.ERROR):
            log_data_access("employee", "123", "delete", "user123", success=False)
            assert len(caplog.records) > 0
            assert any(record.levelno == logging.ERROR for record in caplog.records)

    def test_log_data_access_with_details(self, caplog):
        """Test logging data access with additional details."""
        with caplog.at_level(logging.INFO):
            log_data_access(
                "caces",
                "abc123",
                "view",
                "user456",
                success=True,
                details="Viewed for verification",
            )
            assert len(caplog.records) > 0


class TestLogFileOperation:
    """Tests for log_file_operation function."""

    def test_log_file_upload(self, caplog):
        """Test logging file upload."""
        with caplog.at_level(logging.INFO):
            log_file_operation("upload", "document.pdf", "user123", file_size=1024000)
            assert len(caplog.records) > 0

    def test_log_file_download(self, caplog):
        """Test logging file download."""
        with caplog.at_level(logging.INFO):
            log_file_operation("download", "report.xlsx", "user456", file_size=2048000)
            assert len(caplog.records) > 0

    def test_log_file_delete(self, caplog):
        """Test logging file deletion."""
        with caplog.at_level(logging.INFO):
            log_file_operation("delete", "old_file.pdf", "admin")
            assert len(caplog.records) > 0

    def test_log_failed_file_operation(self, caplog):
        """Test logging failed file operation."""
        with caplog.at_level(logging.ERROR):
            log_file_operation("upload", "large_file.bin", "user123", success=False)
            assert len(caplog.records) > 0
            assert any(record.levelno == logging.ERROR for record in caplog.records)

    def test_log_file_operation_with_details(self, caplog):
        """Test logging file operation with details."""
        with caplog.at_level(logging.INFO):
            log_file_operation(
                "upload", "document.pdf", "user123", details="PDF upload"
            )
            assert len(caplog.records) > 0


class TestRequirePermission:
    """Tests for require_permission decorator."""

    def test_require_permission_with_authenticated_user(self, caplog):
        """Test permission check with authenticated user."""
        # Create mock admin user
        mock_user = MagicMock()
        mock_user.id = "admin123"
        mock_user.is_admin.return_value = True

        with patch("auth.session.get_current_user", return_value=mock_user):
            with caplog.at_level(logging.INFO):

                @require_permission("employee.delete")
                def delete_employee(employee_id):
                    return f"Deleted {employee_id}"

                result = delete_employee("123")
                assert result == "Deleted 123"
                # Should log access granted
                assert len(caplog.records) > 0

    def test_require_permission_with_anonymous_user(self, caplog):
        """Test permission check with anonymous user."""
        with patch("auth.session.get_current_user", return_value=None):
            with caplog.at_level(logging.WARNING):
                with pytest.raises(PermissionError, match="Authentication required"):

                    @require_permission("employee.view")
                    def view_employee(employee_id):
                        return f"Viewing {employee_id}"

                    view_employee("123")

                # Should log access denied
                assert len(caplog.records) > 0

    def test_require_permission_insufficient_permissions(self, caplog):
        """Test permission check with insufficient permissions."""
        # Create mock non-admin user without permissions
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.is_admin.return_value = False
        mock_user.can_manage_employees.return_value = False
        mock_user.can_delete_employees.return_value = False

        with patch("auth.session.get_current_user", return_value=mock_user):
            with caplog.at_level(logging.WARNING):
                with pytest.raises(PermissionError, match="Permission denied"):

                    @require_permission("employee.delete")
                    def delete_employee(employee_id):
                        return f"Deleted {employee_id}"

                    delete_employee("123")

                # Should log access denied
                assert len(caplog.records) > 0


class TestLogSuspiciousActivity:
    """Tests for log_suspicious_activity function."""

    def test_log_suspicious_activity_warning(self, caplog):
        """Test logging suspicious activity with WARNING severity."""
        with caplog.at_level(logging.WARNING):
            log_suspicious_activity(
                "brute_force",
                "Multiple failed login attempts",
                severity="WARNING",
                ip_address="192.168.1.1",
                username="test_user",
            )
            assert len(caplog.records) > 0
            assert any("Suspicious activity" in record.message for record in caplog.records)

    def test_log_suspicious_activity_error(self, caplog):
        """Test logging suspicious activity with ERROR severity."""
        with caplog.at_level(logging.ERROR):
            log_suspicious_activity(
                "sql_injection",
                "Potential SQL injection attempt",
                severity="ERROR",
                ip_address="192.168.1.1",
            )
            assert len(caplog.records) > 0
            assert any(record.levelno == logging.ERROR for record in caplog.records)


class TestSecurityAuditLogger:
    """Tests for SecurityAuditLogger context manager."""

    def test_security_audit_logger_success(self, caplog):
        """Test successful operation logging."""
        with caplog.at_level(logging.INFO):
            with SecurityAuditLogger("data_export", "user123", record_count=100):
                pass  # Operation succeeds

            # Should log both start and complete
            assert len(caplog.records) >= 2

    def test_security_audit_logger_failure(self, caplog):
        """Test failed operation logging."""
        with caplog.at_level(logging.INFO):  # Capture both INFO (start) and ERROR (failed)
            try:
                with SecurityAuditLogger("data_import", "user456"):
                    raise ValueError("Import failed")
            except ValueError:
                pass

            # Should log start and failed events
            assert len(caplog.records) >= 2
            assert any("failed" in record.message for record in caplog.records)

    def test_security_audit_logger_with_context(self, caplog):
        """Test context manager with additional context."""
        with caplog.at_level(logging.INFO):
            with SecurityAuditLogger("backup", "admin", backup_type="full"):
                pass

            assert len(caplog.records) >= 2


# Test constants
def test_event_constants():
    """Test that event constants are defined correctly."""
    assert EVENT_LOGIN == "login"
    assert EVENT_LOGOUT == "logout"
    assert EVENT_FAILED_LOGIN == "failed_login"
    assert EVENT_PASSWORD_CHANGE == "password_change"
    assert EVENT_ACCESS_GRANTED == "access_granted"
    assert EVENT_ACCESS_DENIED == "access_denied"


# Import logging for caplog
import logging
