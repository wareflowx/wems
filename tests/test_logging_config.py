"""Tests for logging configuration module."""

import json
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.logging_config import (
    setup_logging,
    get_logger,
    JSONFormatter,
    log_performance,
    log_security_event,
    log_audit,
    LoggerMixin,
    get_log_dir,
)


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_json_formatter_basic(self):
        """Test basic JSON formatting."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_json_formatter_with_exception(self):
        """Test JSON formatting with exception info."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error occurred",
                args=(),
                exc_info=True,
            )
            record.exc_info = sys.exc_info()
            formatted = formatter.format(record)
            data = json.loads(formatted)

            assert "exception" in data
            assert "ValueError" in data["exception"]

    def test_json_formatter_with_extra_fields(self):
        """Test JSON formatting with extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.user_id = "test-user"
        record.action = "test_action"
        record.duration_ms = 123.45

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["user_id"] == "test-user"
        assert data["action"] == "test_action"
        assert data["duration_ms"] == 123.45


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_default(self, tmp_path):
        """Test logging setup with default parameters."""
        with patch("utils.logging_config.get_log_dir", return_value=tmp_path):
            setup_logging(enable_console=False, enable_file=True)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO
            assert len(root_logger.handlers) == 1

            # Check file handler was created
            handler = root_logger.handlers[0]
            assert isinstance(handler, logging.handlers.RotatingFileHandler)

    def test_setup_logging_debug_level(self, tmp_path):
        """Test logging setup with DEBUG level."""
        with patch("utils.logging_config.get_log_dir", return_value=tmp_path):
            setup_logging(level="DEBUG", enable_console=False, enable_file=True)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG

    def test_setup_logging_console_only(self):
        """Test logging setup with console output only."""
        setup_logging(enable_console=True, enable_file=False)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_file_rotation(self, tmp_path):
        """Test log file rotation parameters."""
        with patch("utils.logging_config.get_log_dir", return_value=tmp_path):
            setup_logging(
                enable_console=False, enable_file=True, max_bytes=1024, backup_count=3
            )

            root_logger = logging.getLogger()
            handler = root_logger.handlers[0]
            assert handler.maxBytes == 1024
            assert handler.backupCount == 3


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"


class TestLogPerformance:
    """Tests for log_performance function."""

    def test_log_performance(self, caplog):
        """Test performance logging."""
        with caplog.at_level(logging.INFO):
            log_performance("test_function", 123.45, user_id="test-user")

            assert len(caplog.records) == 1
            record = caplog.records[0]
            assert "Performance: test_function completed in 123.45ms" in record.message

    def test_log_performance_with_context(self, caplog):
        """Test performance logging with additional context."""
        with caplog.at_level(logging.INFO):
            log_performance(
                "db_query", 50.0, query_type="SELECT", row_count=10, user_id="user1"
            )

            assert len(caplog.records) == 1


class TestLogSecurityEvent:
    """Tests for log_security_event function."""

    def test_log_security_event_default(self, caplog):
        """Test security event logging with default severity."""
        with caplog.at_level(logging.INFO):
            log_security_event("login", "User logged in successfully", user_id="user1")

            assert len(caplog.records) == 1
            record = caplog.records[0]
            assert "Security: login" in record.message

    def test_log_security_event_warning(self, caplog):
        """Test security event logging with WARNING severity."""
        with caplog.at_level(logging.WARNING):
            log_security_event(
                "failed_login", "Invalid password", severity="WARNING", user_id="user1"
            )

            assert len(caplog.records) == 1
            assert caplog.records[0].levelno == logging.WARNING

    def test_log_security_event_error(self, caplog):
        """Test security event logging with ERROR severity."""
        with caplog.at_level(logging.ERROR):
            log_security_event(
                "account_locked",
                "Account locked after 5 failed attempts",
                severity="ERROR",
                user_id="user1",
            )

            assert len(caplog.records) == 1
            assert caplog.records[0].levelno == logging.ERROR


class TestLogAudit:
    """Tests for log_audit function."""

    def test_log_audit(self, caplog):
        """Test audit logging."""
        with caplog.at_level(logging.INFO):
            log_audit(
                action="create",
                entity_type="employee",
                entity_id="123",
                user_id="admin",
            )

            assert len(caplog.records) == 1
            record = caplog.records[0]
            assert "Audit: create on employee:123 by admin" in record.message

    def test_log_audit_with_context(self, caplog):
        """Test audit logging with additional context."""
        with caplog.at_level(logging.INFO):
            log_audit(
                action="delete",
                entity_type="employee",
                entity_id="456",
                user_id="admin",
                reason="Data quality issue",
            )

            assert len(caplog.records) == 1


class TestLoggerMixin:
    """Tests for LoggerMixin class."""

    def test_logger_mixin(self):
        """Test LoggerMixin provides logger property."""

        class TestClass(LoggerMixin):
            pass

        obj = TestClass()
        logger = obj.logger
        assert isinstance(logger, logging.Logger)
        assert logger.name == "TestClass"


class TestGetLogDir:
    """Tests for get_log_dir function."""

    def test_get_log_dir(self, tmp_path):
        """Test log directory creation."""
        with patch("utils.logging_config.get_base_dir", return_value=tmp_path):
            log_dir = get_log_dir()
            assert log_dir == tmp_path / "logs"
            assert log_dir.exists()
            assert log_dir.is_dir()

    def test_get_log_dir_creates_if_not_exists(self, tmp_path):
        """Test log directory is created if it doesn't exist."""
        with patch("utils.logging_config.get_base_dir", return_value=tmp_path):
            log_dir = get_log_dir()
            assert log_dir.exists()

            # Remove and recreate to test idempotency
            log_dir.rmdir()
            log_dir2 = get_log_dir()
            assert log_dir2.exists()
