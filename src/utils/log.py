"""Logger setup and configuration."""

import logging
import os
import socket
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "employee_manager",
    level: str = "INFO",
    log_file: Path | None = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3,
) -> logging.Logger:
    """
    Setup logger with rotating file handler and console output.

    Features:
    - RotatingFileHandler (max 5MB, keep 3 files)
    - Console handler for debugging
    - Formatter with timestamp, level, module, message
    - Application lifecycle logging

    Args:
        name: Logger name (default: "employee_manager")
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file (if None, only console logging)
        max_bytes: Maximum size of each log file before rotation (default: 5MB)
        backup_count: Number of backup files to keep (default: 3)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(level="DEBUG", log_file=Path("app.log"))
        >>> logger.info("Application started")
    """
    # Create logger
    logger = logging.getLogger(name)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set logging level
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_application_start(logger: logging.Logger) -> None:
    """
    Log application startup with system information.

    Logs:
    - Application start message
    - System hostname
    - Username
    - Process ID
    - Python version
    - Start timestamp

    Args:
        logger: Logger instance to use

    Example:
        >>> logger = setup_logger()
        >>> log_application_start(logger)
        # Output: 2026-01-16 10:30:00 | INFO | employee_manager | Application starting...
    """
    logger.info("=" * 60)
    logger.info("Application starting...")
    logger.info(f"  Hostname: {socket.gethostname()}")
    logger.info(f"  Username: {os.environ.get('USERNAME') or os.environ.get('USER', 'unknown')}")
    logger.info(f"  Process ID: {os.getpid()}")
    logger.info(f"  Python Version: {sys.version.split()[0]}")
    logger.info(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def log_application_stop(logger: logging.Logger) -> None:
    """
    Log application shutdown information.

    Logs:
    - Application stop message
    - End timestamp

    Args:
        logger: Logger instance to use

    Example:
        >>> logger = setup_logger()
        >>> log_application_stop(logger)
        # Output: 2026-01-16 10:35:00 | INFO | employee_manager | Application stopped.
    """
    logger.info("=" * 60)
    logger.info("Application stopped.")
    logger.info(f"  End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def log_lock_acquired(logger: logging.Logger, hostname: str, pid: int) -> None:
    """
    Log when application lock is acquired.

    Args:
        logger: Logger instance to use
        hostname: Hostname that acquired the lock
        pid: Process ID that acquired the lock

    Example:
        >>> logger = setup_logger()
        >>> log_lock_acquired(logger, "PC-01", 12345)
        # Output: 2026-01-16 10:30:00 | INFO | employee_manager | Lock acquired by PC-01 (PID: 12345)
    """
    logger.info(f"Lock acquired by {hostname} (PID: {pid})")


def log_lock_released(logger: logging.Logger, hostname: str, pid: int) -> None:
    """
    Log when application lock is released.

    Args:
        logger: Logger instance to use
        hostname: Hostname that released the lock
        pid: Process ID that released the lock

    Example:
        >>> logger = setup_logger()
        >>> log_lock_released(logger, "PC-01", 12345)
        # Output: 2026-01-16 10:35:00 | INFO | employee_manager | Lock released by PC-01 (PID: 12345)
    """
    logger.info(f"Lock released by {hostname} (PID: {pid})")


def log_lock_lost(logger: logging.Logger, hostname: str) -> None:
    """
    Log when lock is lost (heartbeat failure).

    Args:
        logger: Logger instance to use
        hostname: Hostname that lost the lock

    Example:
        >>> logger = setup_logger()
        >>> log_lock_lost(logger, "PC-01")
        # Output: 2026-01-16 10:35:00 | CRITICAL | employee_manager | Lock lost for PC-01!
    """
    logger.critical(f"Lock lost for {hostname}!")


def log_database_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log database error with context.

    Args:
        logger: Logger instance to use
        error: Exception that occurred
        context: Optional context string

    Example:
        >>> try:
        ...     # database operation
        ... except Exception as e:
        ...     log_database_error(logger, e, "fetching employees")
    """
    msg = "Database error"
    if context:
        msg += f" ({context})"
    msg += f": {error}"
    logger.error(msg)


def log_file_operation(logger: logging.Logger, operation: str, file_path: Path, success: bool) -> None:
    """
    Log file operation result.

    Args:
        logger: Logger instance to use
        operation: Operation type (copy, delete, etc.)
        file_path: Path to the file
        success: Whether operation succeeded

    Example:
        >>> log_file_operation(logger, "copy", Path("/path/to/file.pdf"), True)
        # Output: 2026-01-16 10:30:00 | INFO | employee_manager | File copy successful: /path/to/file.pdf
    """
    status = "successful" if success else "failed"
    level = logger.info if success else logger.error
    level(f"File {operation} {status}: {file_path}")


# Convenience function for getting a logger instance
def get_logger(name: str = "employee_manager") -> logging.Logger:
    """
    Get or create a logger instance.

    This is a convenience function that returns an existing logger
    or creates a new one with default settings.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        logger = setup_logger(name=name, level="INFO")

    return logger
