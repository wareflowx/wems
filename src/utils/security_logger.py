"""Security event logging utilities.

This module provides functions and decorators for logging
security-related events, including:
- Authentication events (login, logout, failed attempts)
- Authorization events (permission checks, access denials)
- Data access events (view, modify, delete)
- Suspicious activity detection
- Security audit trail
"""

import functools
from typing import Callable, Optional, Any
from datetime import datetime

from utils.logging_config import log_security_event, get_logger


logger = get_logger(__name__)


# Security event types
EVENT_LOGIN = "login"
EVENT_LOGOUT = "logout"
EVENT_FAILED_LOGIN = "failed_login"
EVENT_PASSWORD_CHANGE = "password_change"
EVENT_PASSWORD_RESET = "password_reset"
EVENT_ACCOUNT_LOCKED = "account_locked"
EVENT_ACCOUNT_UNLOCKED = "account_unlocked"

EVENT_PERMISSION_CHECK = "permission_check"
EVENT_ACCESS_GRANTED = "access_granted"
EVENT_ACCESS_DENIED = "access_denied"

EVENT_DATA_VIEW = "data_view"
EVENT_DATA_CREATE = "data_create"
EVENT_DATA_UPDATE = "data_update"
EVENT_DATA_DELETE = "data_delete"

EVENT_FILE_UPLOAD = "file_upload"
EVENT_FILE_DOWNLOAD = "file_download"
EVENT_FILE_DELETE = "file_delete"

EVENT_CONFIG_CHANGE = "config_change"
EVENT_SECURITY_SCAN = "security_scan"


def log_authentication(
    event_type: str,
    username: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[str] = None,
):
    """
    Log authentication-related events.

    Args:
        event_type: Type of auth event (login, logout, failed_login, etc.)
        username: Username attempting authentication
        success: Whether the operation succeeded
        ip_address: IP address of the request (optional)
        user_agent: User agent string (optional)
        details: Additional details (optional)

    Example:
        log_authentication("login", "john_doe", True, ip_address="192.168.1.1")
    """
    severity = "INFO" if success else "WARNING"
    description = f"Authentication {event_type} for {username}"

    if not success:
        if event_type == EVENT_FAILED_LOGIN:
            description = f"Failed login attempt for {username}"
        severity = "WARNING"

    if details:
        description += f": {details}"

    context = {
        "username": username,
        "success": success,
    }

    if ip_address:
        context["ip_address"] = ip_address
    if user_agent:
        context["user_agent"] = user_agent[:200]  # Truncate long user agents

    log_security_event(event_type, description, severity, **context)


def log_authorization(
    resource: str,
    action: str,
    user_id: str,
    granted: bool,
    reason: Optional[str] = None,
):
    """
    Log authorization/access control events.

    Args:
        resource: Resource being accessed (e.g., "employee", "caces")
        action: Action being performed (e.g., "view", "edit", "delete")
        user_id: ID of user attempting access
        granted: Whether access was granted
        reason: Reason for denial (if applicable)

    Example:
        log_authorization("employee", "delete", "user123", granted=False,
                         reason="Insufficient permissions")
    """
    severity = "INFO" if granted else "WARNING"
    status = "granted" if granted else "denied"
    description = f"Access {status} for {action} on {resource}"

    if not granted and reason:
        description += f": {reason}"

    context = {
        "resource": resource,
        "action": action,
        "user_id": user_id,
        "granted": granted,
    }

    log_security_event(
        EVENT_ACCESS_GRANTED if granted else EVENT_ACCESS_DENIED,
        description,
        severity,
        **context,
    )


def log_data_access(
    entity_type: str,
    entity_id: str,
    action: str,
    user_id: str,
    success: bool = True,
    details: Optional[str] = None,
):
    """
    Log data access events for audit trail.

    Args:
        entity_type: Type of entity (employee, caces, medical_visit, etc.)
        entity_id: ID of the entity
        action: Action performed (view, create, update, delete)
        user_id: ID of user performing action
        success: Whether operation succeeded
        details: Additional details

    Example:
        log_data_access("employee", "123", "view", "user456")
    """
    severity = "INFO" if success else "ERROR"
    description = f"Data {action} on {entity_type}:{entity_id} by {user_id}"

    if not success:
        description += " (FAILED)"

    if details:
        description += f": {details}"

    event_map = {
        "view": EVENT_DATA_VIEW,
        "create": EVENT_DATA_CREATE,
        "update": EVENT_DATA_UPDATE,
        "delete": EVENT_DATA_DELETE,
    }

    event_type = event_map.get(action, f"data_{action}")

    context = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "user_id": user_id,
        "success": success,
    }

    log_security_event(event_type, description, severity, **context)


def log_file_operation(
    operation: str,
    filename: str,
    user_id: str,
    success: bool = True,
    file_size: Optional[int] = None,
    details: Optional[str] = None,
):
    """
    Log file operations for security monitoring.

    Args:
        operation: Operation type (upload, download, delete)
        filename: Name of the file
        user_id: ID of user performing operation
        success: Whether operation succeeded
        file_size: Size of file in bytes (optional)
        details: Additional details (optional)

    Example:
        log_file_operation("upload", "document.pdf", "user123",
                          file_size=1024000)
    """
    severity = "INFO" if success else "ERROR"
    description = f"File {operation} of '{filename}' by {user_id}"

    if not success:
        description += " (FAILED)"

    if file_size:
        description += f" ({file_size} bytes)"

    if details:
        description += f": {details}"

    event_map = {
        "upload": EVENT_FILE_UPLOAD,
        "download": EVENT_FILE_DOWNLOAD,
        "delete": EVENT_FILE_DELETE,
    }

    event_type = event_map.get(operation, f"file_{operation}")

    context = {
        "file_name": filename,  # Renamed to avoid LogRecord conflicts
        "user_id": user_id,
        "operation": operation,
        "success": success,
    }

    if file_size:
        context["file_size"] = file_size

    log_security_event(event_type, description, severity, **context)


def require_permission(permission: str) -> Callable:
    """
    Decorator to require specific permission for function execution.

    Logs authorization attempts and raises exception if permission denied.

    Args:
        permission: Required permission string

    Example:
        @require_permission("employee.delete")
        def delete_employee(employee_id):
            pass

    Raises:
        PermissionError: If user lacks required permission
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user from session
            from auth.session import get_current_user

            user = get_current_user()

            if user is None:
                log_authorization(
                    resource=func.__name__,
                    action=permission,
                    user_id="anonymous",
                    granted=False,
                    reason="Not authenticated",
                )
                raise PermissionError("Authentication required")

            # Check permission (simplified - in production, use proper permission system)
            has_permission = _check_user_permission(user, permission)

            if not has_permission:
                log_authorization(
                    resource=func.__name__,
                    action=permission,
                    user_id=str(user.id),
                    granted=False,
                    reason=f"Missing permission: {permission}",
                )
                raise PermissionError(f"Permission denied: {permission}")

            # Log access granted
            log_authorization(
                resource=func.__name__,
                action=permission,
                user_id=str(user.id),
                granted=True,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_suspicious_activity(
    activity_type: str,
    description: str,
    severity: str = "WARNING",
    **context,
):
    """
    Log suspicious or potentially malicious activity.

    Args:
        activity_type: Type of suspicious activity
        description: Description of the activity
        severity: Severity level (WARNING, ERROR)
        **context: Additional context (ip_address, user_id, etc.)

    Example:
        log_suspicious_activity("brute_force",
                               "Multiple failed login attempts",
                               ip_address="192.168.1.1",
                               username="test_user")
    """
    log_security_event(
        f"suspicious_{activity_type}",
        f"Suspicious activity detected: {description}",
        severity,
        **context,
    )


def _check_user_permission(user, permission: str) -> bool:
    """
    Check if user has specific permission.

    This is a simplified implementation. In production,
    use a proper permission system with roles and capabilities.

    Args:
        user: User object
        permission: Permission string to check

    Returns:
        True if user has permission, False otherwise
    """
    # Admin has all permissions
    if user.is_admin():
        return True

    # Simple permission check based on role
    # In production, use a more sophisticated permission system
    if "employee." in permission:
        return user.can_manage_employees()

    if "delete" in permission:
        return user.can_delete_employees()

    return False


class SecurityAuditLogger:
    """Context manager for logging security-related operations."""

    def __init__(self, operation: str, user_id: str, **context):
        """
        Initialize security audit logger.

        Args:
            operation: Operation being performed
            user_id: ID of user performing operation
            **context: Additional context
        """
        self.operation = operation
        self.user_id = user_id
        self.context = context
        self.success = False

    def __enter__(self):
        """Enter context - log operation start."""
        log_security_event(
            f"{self.operation}_start",
            f"Starting {self.operation}",
            "INFO",
            user_id=self.user_id,
            **self.context,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - log operation result."""
        self.success = exc_type is None

        if self.success:
            log_security_event(
                f"{self.operation}_complete",
                f"Completed {self.operation} successfully",
                "INFO",
                user_id=self.user_id,
                **self.context,
            )
        else:
            log_security_event(
                f"{self.operation}_failed",
                f"{self.operation} failed: {exc_val}",
                "ERROR",
                user_id=self.user_id,
                **self.context,
            )
        return False  # Don't suppress exceptions
