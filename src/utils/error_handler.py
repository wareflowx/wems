"""
Error Handler Module

Provides centralized error handling with:
- Custom exception hierarchy
- Error categorization
- Structured logging
- User-friendly error messages
- Recovery mechanisms
"""

import logging
import sys
from enum import Enum
from typing import Optional, Callable
from pathlib import Path

# Setup logging configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "wareflow_ems.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors for different handling."""
    USER_ERROR = "user"                # User input validation errors
    VALIDATION_ERROR = "validation"     # Data validation failures
    DATABASE_ERROR = "database"         # Database connectivity/errors
    FILE_ERROR = "file"                 # File system operations
    NETWORK_ERROR = "network"           # Network-related errors
    PERMISSION_ERROR = "permission"     # File/system permissions
    CRITICAL_ERROR = "critical"         # System-level errors
    UNKNOWN_ERROR = "unknown"           # Unclassified errors


class ApplicationError(Exception):
    """Base class for all application errors."""

    def __init__(self, message: str, context: str = ""):
        """
        Initialize application error.

        Args:
            message: Error message
            context: Additional context about where error occurred
        """
        self.message = message
        self.context = context
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Data validation failed."""

    def __init__(self, message: str, field: str = None, value=None):
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field name that failed validation
            value: Value that failed validation
        """
        self.field = field
        self.value = value
        super().__init__(message)


class DatabaseError(ApplicationError):
    """Database operation failed."""

    def __init__(self, message: str, query: str = None):
        """
        Initialize database error.

        Args:
            message: Error message
            query: Query that failed
        """
        self.query = query
        super().__init__(message)


class FilePermissionError(ApplicationError):
    """File permission or access error."""

    def __init__(self, message: str, path: Path = None):
        """
        Initialize file permission error.

        Args:
            message: Error message
            path: File path that caused error
        """
        self.path = path
        super().__init__(message)


class DataNotFoundError(ApplicationError):
    """Requested data not found."""

    def __init__(self, message: str, resource_type: str = None, resource_id: str = None):
        """
        Initialize data not found error.

        Args:
            message: Error message
            resource_type: Type of resource (e.g., "Employee")
            resource_id: ID of resource
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message)


def categorize_error(error: Exception) -> ErrorCategory:
    """
    Categorize error by type.

    Args:
        error: The exception to categorize

    Returns:
        ErrorCategory enum value
    """
    if isinstance(error, (ValidationError, ValueError)):
        return ErrorCategory.VALIDATION_ERROR
    elif isinstance(error, DatabaseError):
        return ErrorCategory.DATABASE_ERROR
    elif isinstance(error, FilePermissionError):
        return ErrorCategory.PERMISSION_ERROR
    elif isinstance(error, DataNotFoundError):
        return ErrorCategory.USER_ERROR
    elif isinstance(error, (FileNotFoundError, PermissionError)):
        return ErrorCategory.FILE_ERROR
    elif isinstance(error, (ConnectionError, TimeoutError)):
        return ErrorCategory.NETWORK_ERROR
    elif isinstance(error, (OSError, IOError)):
        return ErrorCategory.FILE_ERROR
    elif isinstance(error, ApplicationError):
        # Check error message for specific patterns
        error_str = str(error).lower()
        if "permission denied" in error_str or "access denied" in error_str:
            return ErrorCategory.PERMISSION_ERROR
        if "not found" in error_str:
            return ErrorCategory.USER_ERROR
        return ErrorCategory.UNKNOWN_ERROR
    else:
        return ErrorCategory.UNKNOWN_ERROR


def handle_error(
    error: Exception,
    context: str = "",
    show_to_user: bool = True,
    on_recovery: Optional[Callable] = None,
    reraise: bool = False
):
    """
    Centralized error handling with proper categorization.

    Args:
        error: The exception that occurred
        context: Where the error occurred (function name, operation)
        show_to_user: Whether to show error to user
        on_recovery: Optional callback to attempt recovery
        reraise: Whether to reraise the exception after handling

    Raises:
        Exception: If reraise=True
    """
    # Categorize error
    error_type = categorize_error(error)

    # Build full error message
    full_message = f"{context}: {error}" if context else str(error)

    # Log with appropriate level
    if error_type == ErrorCategory.CRITICAL_ERROR:
        logging.critical(full_message, exc_info=True)
    elif error_type == ErrorCategory.DATABASE_ERROR:
        logging.error(full_message, exc_info=True)
    elif error_type == ErrorCategory.PERMISSION_ERROR:
        logging.error(full_message, exc_info=True)
    elif error_type == ErrorCategory.FILE_ERROR:
        logging.warning(full_message)
    elif error_type == ErrorCategory.VALIDATION_ERROR:
        logging.info(full_message)
    elif error_type == ErrorCategory.USER_ERROR:
        logging.info(full_message)
    elif error_type == ErrorCategory.NETWORK_ERROR:
        logging.warning(full_message)
    else:
        logging.error(full_message, exc_info=True)

    # Show to user if needed
    if show_to_user:
        try:
            show_error_to_user(error, error_type)
        except Exception as e:
            logging.error(f"Failed to show error to user: {e}")

    # Attempt recovery if possible
    if on_recovery:
        try:
            on_recovery(error)
        except Exception as recovery_error:
            logging.error(f"Recovery failed: {recovery_error}")

    # Reraise if requested
    if reraise:
        raise error


def show_error_to_user(error: Exception, error_type: ErrorCategory):
    """
    Show appropriate error message to user.

    Args:
        error: The exception to display
        error_type: Category of the error
    """
    try:
        from tkinter import messagebox
    except ImportError:
        # Fallback if tkinter not available
        print(f"[ERROR] {error}")
        return

    # Determine severity and icon
    if error_type == ErrorCategory.CRITICAL_ERROR:
        icon = "error"
        title = "Critical Error"
    elif error_type == ErrorCategory.DATABASE_ERROR:
        icon = "error"
        title = "Database Error"
    elif error_type == ErrorCategory.PERMISSION_ERROR:
        icon = "error"
        title = "Permission Error"
    elif error_type == ErrorCategory.FILE_ERROR:
        icon = "warning"
        title = "File Error"
    elif error_type == ErrorCategory.VALIDATION_ERROR:
        icon = "info"
        title = "Validation Error"
    elif error_type == ErrorCategory.USER_ERROR:
        icon = "info"
        title = "Information"
    elif error_type == ErrorCategory.NETWORK_ERROR:
        icon = "warning"
        title = "Network Error"
    else:
        icon = "info"
        title = "Error"

    # Format user-friendly message
    user_message = format_user_message(error)

    # Show message
    try:
        if error_type in [ErrorCategory.CRITICAL_ERROR, ErrorCategory.DATABASE_ERROR, ErrorCategory.PERMISSION_ERROR]:
            messagebox.showerror(title, user_message, icon=icon)
        elif error_type in [ErrorCategory.FILE_ERROR, ErrorCategory.NETWORK_ERROR]:
            messagebox.showwarning(title, user_message, icon=icon)
        else:
            messagebox.showinfo(title, user_message, icon=icon)
    except Exception as e:
        logging.error(f"Failed to show message box: {e}")
        print(f"[{title}] {user_message}")


def format_user_message(error: Exception) -> str:
    """
    Format error message for user consumption.

    Args:
        error: The exception to format

    Returns:
        User-friendly error message
    """
    error_str = str(error)

    # Check for specific error types
    if isinstance(error, ValidationError):
        if error.field:
            return f"Validation failed for '{error.field}': {error.message}"
        return f"Validation error: {error.message}"

    if isinstance(error, DatabaseError):
        return "A database error occurred. Please try again. If the problem persists, contact support."

    if isinstance(error, FilePermissionError):
        if error.path:
            return f"Permission denied accessing: {error.path}"
        return "You don't have permission to perform this operation."

    if isinstance(error, DataNotFoundError):
        if error.resource_type and error.resource_id:
            return f"{error.resource_type} '{error.resource_id}' not found."
        return "The requested data was not found."

    # Generic error messages based on error string
    error_lower = error_str.lower()

    if "permission denied" in error_lower:
        return "You don't have permission to perform this operation."

    if "not found" in error_lower:
        return error_str  # Already user-friendly

    if "duplicate" in error_lower or "unique" in error_lower:
        return "This record already exists. Please use a different identifier."

    if "foreign key" in error_lower:
        return "Cannot delete this record because it is referenced by other records."

    if "database" in error_lower or "sqlite" in error_lower:
        return "A database error occurred. Please try again."

    # Default: return original message
    return error_str


def safe_execute(
    func: Callable,
    *args,
    context: str = "",
    show_to_user: bool = True,
    on_error: Optional[Callable] = None,
    default_return=None,
    **kwargs
):
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments for function
        context: Context description for error logging
        show_to_user: Whether to show errors to user
        on_error: Optional callback on error
        default_return: Value to return on error
        **kwargs: Keyword arguments for function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context=context, show_to_user=show_to_user, on_recovery=on_error)
        return default_return


def log_and_reraise(
    error: Exception,
    context: str = "",
    message: str = ""
):
    """
    Log error and reraise for caller to handle.

    Args:
        error: The exception to log
        context: Where the error occurred
        message: Additional message

    Raises:
        Exception: The original error is reraised
    """
    full_message = f"{context}: {message}" if message else context
    full_message = f"{full_message} - {error}" if full_message else str(error)

    logging.error(full_message, exc_info=True)
    raise error


class ErrorBoundary:
    """
    Context manager for catching and handling errors in a block of code.

    Usage:
        with ErrorBoundary("operation_name", show_to_user=True):
            risky_operation()
    """

    def __init__(
        self,
        context: str = "",
        show_to_user: bool = True,
        on_error: Optional[Callable] = None,
        default_return=None
    ):
        """
        Initialize error boundary.

        Args:
            context: Context description
            show_to_user: Whether to show errors to user
            on_error: Optional callback on error
            default_return: Value to return on error
        """
        self.context = context
        self.show_to_user = show_to_user
        self.on_error = on_error
        self.default_return = default_return

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager and handle any exception.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            True to suppress exception, False to propagate
        """
        if exc_type is not None:
            handle_error(
                exc_val,
                context=self.context,
                show_to_user=self.show_to_user,
                on_recovery=self.on_error
            )
            # Suppress exception
            return True
        return False
