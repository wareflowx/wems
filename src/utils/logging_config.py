"""Logging configuration for Wareflow EMS.

This module provides structured logging configuration with support for:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- JSON-formatted logs for parsing and analysis
- File rotation to prevent unbounded log growth
- Console and file output
- Application-specific loggers (performance, security, audit)
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import json


def get_base_dir() -> Path:
    """
    Get the base directory for the application.

    Returns:
        Path to base directory (src parent)
    """
    # Get the directory containing this file
    current_dir = Path(__file__).parent
    # Go up to src directory
    src_dir = current_dir.parent
    # Base directory is src's parent
    return src_dir.parent


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        return json.dumps(log_data)


def get_log_dir() -> Path:
    """Get the log directory path.

    Returns:
        Path to logs directory
    """
    log_dir = get_base_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> None:
    """
    Configure application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable console output
        enable_file: Enable file output
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    # Get numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create JSON formatter
    json_formatter = JSONFormatter()

    # Add console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(json_formatter)
        root_logger.addHandler(console_handler)

    # Add file handler with rotation
    if enable_file:
        log_dir = get_log_dir()
        log_file = log_dir / "app.log"

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

    # Suppress overly verbose third-party loggers
    logging.getLogger("peewee").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin to add logging capability to classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)


# Performance logging
def log_performance(func_name: str, duration_ms: float, **kwargs):
    """
    Log performance metrics.

    Args:
        func_name: Name of function/method
        duration_ms: Duration in milliseconds
        **kwargs: Additional context (user_id, query_type, etc.)
    """
    logger = get_logger("performance")
    logger.info(
        f"Performance: {func_name} completed in {duration_ms:.2f}ms",
        extra={
            "action": "performance",
            "function": func_name,
            "duration_ms": duration_ms,
            **kwargs,
        },
    )


# Security logging
def log_security_event(
    event_type: str,
    description: str,
    severity: str = "INFO",
    **kwargs,
):
    """
    Log security-related events.

    Args:
        event_type: Type of security event (login, logout, failed_login, etc.)
        description: Human-readable description
        severity: Event severity (INFO, WARNING, ERROR)
        **kwargs: Additional context (user_id, ip_address, etc.)
    """
    logger = get_logger("security")
    numeric_severity = getattr(logging, severity.upper(), logging.INFO)

    logger.log(
        numeric_severity,
        f"Security: {event_type} - {description}",
        extra={
            "action": "security",
            "event_type": event_type,
            **kwargs,
        },
    )


# Audit logging
def log_audit(action: str, entity_type: str, entity_id: str, user_id: str, **kwargs):
    """
    Log audit trail for compliance.

    Args:
        action: Action performed (create, update, delete, view)
        entity_type: Type of entity (employee, caces, medical_visit)
        entity_id: ID of affected entity
        user_id: ID of user performing action
        **kwargs: Additional context
    """
    logger = get_logger("audit")
    logger.info(
        f"Audit: {action} on {entity_type}:{entity_id} by {user_id}",
        extra={
            "action": "audit",
            "audit_action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            **kwargs,
        },
    )
