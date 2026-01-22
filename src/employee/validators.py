"""Data validation logic for Employee entity.

This module provides structured validation for all employee-related data,
including external IDs, dates, certifications, and medical visits.

Validators can be used at multiple layers:
- Application layer (CLI, UI) for early validation with clear error messages
- Model layer (before_save hooks) for guaranteed data integrity
"""

import re
from datetime import date
from pathlib import Path
from typing import Any, Optional

from peewee import Model

from .constants import (
    CACES_TYPES,
    VisitResult,
    VisitType,
)

# =============================================================================
# EXCEPTIONS
# =============================================================================


class ValidationError(Exception):
    """
    Structured exception for validation errors.

    This exception provides detailed information about validation failures,
    making it easy to display clear error messages to users and log
    detailed information for debugging.

    Attributes:
        field: Name of the field that failed validation
        value: The invalid value that was provided
        message: Human-readable error message
        details: Optional dictionary with additional context

    Example:
        >>> raise ValidationError(
        ...     field="external_id",
        ...     value="../etc/passwd",
        ...     message="Path traversal detected",
        ...     details={"pattern": "^[A-Za-z0-9_-]{3,50}$"}
        ... )
    """

    def __init__(self, field: str, value: Any, message: str, details: dict = None):
        self.field = field
        self.value = value
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        """Return formatted error message."""
        base_msg = f"Validation failed for field '{self.field}': {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base_msg} ({details_str})"
        return base_msg

    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            "field": self.field,
            "value": str(self.value) if self.value is not None else None,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# VALIDATOR FUNCTIONS
# =============================================================================


def validate_external_id(external_id: str) -> str:
    """
    Validate the format of an employee's external ID.

    The external ID is used to reference the employee in external systems
    (e.g., WMS). It must follow strict formatting rules to avoid conflicts
    and security issues.

    Validation Rules:
        - Length: 3 to 50 characters
        - Allowed characters: Letters (A-Za-z), numbers (0-9), underscore (_), hyphen (-)
        - No spaces or special characters
        - Protection against path traversal attacks

    Args:
        external_id: External ID to validate (e.g., "WMS-001", "R489-1A")

    Returns:
        The validated external ID (unchanged if valid)

    Raises:
        ValidationError: If the format is invalid

    Examples:
        >>> validate_external_id("WMS-001")
        'WMS-001'
        >>> validate_external_id("R489_1A")
        'R489_1A'
        >>> validate_external_id("../etc/passwd")
        Traceback (most recent call last):
            ...
        ValidationError: Path traversal detected in external_id
    """
    if not external_id:
        raise ValidationError(field="external_id", value=external_id, message="External ID cannot be empty")

    if not isinstance(external_id, str):
        raise ValidationError(field="external_id", value=external_id, message="External ID must be a string")

    # Check length
    if len(external_id) < 3:
        raise ValidationError(
            field="external_id",
            value=external_id,
            message="External ID is too short (minimum 3 characters)",
            details={"min_length": 3, "actual_length": len(external_id)},
        )

    if len(external_id) > 50:
        raise ValidationError(
            field="external_id",
            value=external_id,
            message="External ID is too long (maximum 50 characters)",
            details={"max_length": 50, "actual_length": len(external_id)},
        )

    # Check for path traversal patterns
    path_traversal_patterns = ["../", "..\\", "./", ".\\", "/", "\\"]
    for pattern in path_traversal_patterns:
        if pattern in external_id:
            raise ValidationError(
                field="external_id",
                value=external_id,
                message="Path traversal detected in external_id",
                details={"forbidden_pattern": pattern},
            )

    # Check for valid characters (alphanumeric, underscore, hyphen)
    pattern = r"^[A-Za-z0-9_-]+$"
    if not re.match(pattern, external_id):
        raise ValidationError(
            field="external_id",
            value=external_id,
            message="External ID contains invalid characters",
            details={"allowed_pattern": pattern, "allowed_chars": "Letters, numbers, underscore (_), hyphen (-)"},
        )

    return external_id


def validate_entry_date(entry_date: date) -> date:
    """
    Validate an employee's entry date.

    The entry date represents when an employee joined the company.
    It must be a reasonable date and cannot be in the future.

    Validation Rules:
        - Date cannot be in the future
        - Date must be >= 1900-01-01 (reasonable lower bound)
        - Date must be provided (not None)

    Args:
        entry_date: Entry date to validate

    Returns:
        The validated entry date

    Raises:
        ValidationError: If the date is invalid

    Examples:
        >>> from datetime import date
        >>> validate_entry_date(date(2020, 1, 15))
        datetime.date(2020, 1, 15)
        >>> validate_entry_date(date(2100, 1, 1))
        Traceback (most recent call last):
            ...
        ValidationError: Entry date cannot be in the future
    """
    if not entry_date:
        raise ValidationError(field="entry_date", value=entry_date, message="Entry date is required")

    if not isinstance(entry_date, date):
        raise ValidationError(field="entry_date", value=entry_date, message="Entry date must be a date object")

    # Check if date is in the future
    if entry_date > date.today():
        raise ValidationError(
            field="entry_date",
            value=entry_date,
            message="Entry date cannot be in the future",
            details={"entry_date": entry_date.isoformat(), "current_date": date.today().isoformat()},
        )

    # Check if date is too old (before 1900)
    min_date = date(1900, 1, 1)
    if entry_date < min_date:
        raise ValidationError(
            field="entry_date",
            value=entry_date,
            message="Entry date is too old (minimum 1900-01-01)",
            details={"min_date": min_date.isoformat(), "actual_date": entry_date.isoformat()},
        )

    return entry_date


def validate_caces_kind(kind: str) -> str:
    """
    Validate CACES certification type.

    CACES certifications must be one of the recognized types defined
    in the CACES_TYPES constant.

    Args:
        kind: CACES certification type to validate

    Returns:
        The validated CACES type

    Raises:
        ValidationError: If the type is not recognized

    Examples:
        >>> validate_caces_kind("R489-1A")
        'R489-1A'
        >>> validate_caces_kind("R489-5")
        'R489-5'
        >>> validate_caces_kind("R489-2")
        Traceback (most recent call last):
            ...
        ValidationError: Invalid CACES type
    """
    if not kind:
        raise ValidationError(field="kind", value=kind, message="CACES type is required")

    if not isinstance(kind, str):
        raise ValidationError(field="kind", value=kind, message="CACES type must be a string")

    kind_upper = kind.upper()

    if kind_upper not in CACES_TYPES:
        raise ValidationError(
            field="kind",
            value=kind,
            message="Invalid CACES type",
            details={"provided": kind, "allowed_types": CACES_TYPES},
        )

    return kind_upper


def validate_medical_visit_consistency(visit_type: str, result: str) -> tuple:
    """
    Validate consistency between medical visit type and result.

    This validator ensures that certain visit types have appropriate results.
    For example, a "recovery" visit (visite de reprise) must result in
    "fit_with_restrictions" because an employee returning after medical
    absence typically has work restrictions.

    Validation Rules:
        - visit_type must be in VisitType.ALL
        - result must be in VisitResult.ALL
        - If visit_type is "recovery", result MUST be "fit_with_restrictions"

    Args:
        visit_type: Type of medical visit (initial, periodic, recovery)
        result: Result of the visit (fit, unfit, fit_with_restrictions)

    Returns:
        Tuple of (visit_type, result) validated

    Raises:
        ValidationError: If the combination is invalid

    Examples:
        >>> validate_medical_visit_consistency("initial", "fit")
        ('initial', 'fit')
        >>> validate_medical_visit_consistency("recovery", "fit_with_restrictions")
        ('recovery', 'fit_with_restrictions')
        >>> validate_medical_visit_consistency("recovery", "fit")
        Traceback (most recent call last):
            ...
        ValidationError: Recovery visits must have restrictions
    """
    # Validate visit type
    if not visit_type:
        raise ValidationError(field="visit_type", value=visit_type, message="Visit type is required")

    if visit_type not in VisitType.ALL:
        raise ValidationError(
            field="visit_type",
            value=visit_type,
            message="Invalid visit type",
            details={"provided": visit_type, "allowed_types": VisitType.ALL},
        )

    # Validate result
    if not result:
        raise ValidationError(field="result", value=result, message="Visit result is required")

    if result not in VisitResult.ALL:
        raise ValidationError(
            field="result",
            value=result,
            message="Invalid visit result",
            details={"provided": result, "allowed_results": VisitResult.ALL},
        )

    # Business rule: Recovery visits must have restrictions
    if visit_type == "recovery" and result != "fit_with_restrictions":
        raise ValidationError(
            field="result",
            value=result,
            message="Recovery visits must result in 'fit_with_restrictions'",
            details={
                "visit_type": visit_type,
                "result": result,
                "expected_result": "fit_with_restrictions",
                "reason": "Employees returning from medical absence typically have work restrictions",
            },
        )

    return visit_type, result


def validate_path_safe(file_path: str, allowed_extensions: Optional[list] = None) -> str:
    """
    Validate that a file path is safe (no path traversal attacks).

    This validator prevents path traversal attacks by checking for dangerous
    patterns in file paths. It also optionally validates file extensions.

    Validation Rules:
        - No path traversal patterns (../, ..\\, ./, .\\)
        - No absolute paths (must be relative)
        - Optional: File extension must be in allowed list

    Args:
        file_path: File path to validate
        allowed_extensions: Optional list of allowed extensions (e.g., [".pdf", ".jpg"])

    Returns:
        The validated file path

    Raises:
        ValidationError: If the path is dangerous

    Examples:
        >>> validate_path_safe("documents/caces.pdf")
        'documents/caces.pdf'
        >>> validate_path_safe("../../../etc/passwd")
        Traceback (most recent call last):
            ...
        ValidationError: Path traversal detected
        >>> validate_path_safe("document.exe", allowed_extensions=[".pdf"])
        Traceback (most recent call last):
            ...
        ValidationError: File extension not allowed
    """
    if not file_path:
        raise ValidationError(field="file_path", value=file_path, message="File path cannot be empty")

    if not isinstance(file_path, str):
        raise ValidationError(field="file_path", value=file_path, message="File path must be a string")

    # Check for path traversal patterns
    path_traversal_patterns = ["../", "..\\", "./", ".\\"]
    for pattern in path_traversal_patterns:
        if pattern in file_path:
            raise ValidationError(
                field="file_path",
                value=file_path,
                message="Path traversal detected",
                details={"forbidden_pattern": pattern},
            )

    # Check for absolute paths (Windows and Unix)
    if re.match(r"^[A-Za-z]:", file_path) or file_path.startswith("/"):
        raise ValidationError(
            field="file_path",
            value=file_path,
            message="Absolute paths are not allowed",
            details={"reason": "Only relative paths are allowed for security"},
        )

    # Check file extension if provided
    if allowed_extensions:
        path_obj = Path(file_path)
        extension = path_obj.suffix.lower()

        if not extension:
            raise ValidationError(
                field="file_path",
                value=file_path,
                message="File has no extension",
                details={"allowed_extensions": allowed_extensions},
            )

        if extension not in allowed_extensions:
            raise ValidationError(
                field="file_path",
                value=file_path,
                message="File extension not allowed",
                details={"provided_extension": extension, "allowed_extensions": allowed_extensions},
            )

    return file_path


# =============================================================================
# VALIDATOR CLASSES
# =============================================================================


class UniqueValidator:
    """
    Reusable uniqueness validator for Peewee models.

    This validator checks that a field value is unique within a database table.
    It can optionally exclude a specific instance (useful for updates).

    Attributes:
        model_class: The Peewee model class to validate against
        field: The field to check for uniqueness
        exclude_instance: Instance to exclude from uniqueness check (for updates)

    Examples:
        >>> # Check for new record
        >>> validator = UniqueValidator(Employee, Employee.external_id)
        >>> validator.validate("WMS-001")  # OK if doesn't exist
        >>> validator.validate("WMS-001")  # Raises ValidationError if exists

        >>> # Check for update (exclude current instance)
        >>> employee = Employee.get_by_id(1)
        >>> validator = UniqueValidator(Employee, Employee.external_id, exclude_instance=employee)
        >>> validator.validate(employee.external_id)  # OK - excludes itself
    """

    def __init__(self, model_class: type[Model], field, exclude_instance: Optional[Model] = None):
        """
        Initialize the unique validator.

        Args:
            model_class: Peewee model class
            field: Field object to check for uniqueness
            exclude_instance: Optional instance to exclude from check
        """
        self.model_class = model_class
        self.field = field
        self.exclude_instance = exclude_instance

    def validate(self, value: Any) -> Any:
        """
        Validate that the value is unique in the database.

        Args:
            value: Value to check for uniqueness

        Returns:
            The value if unique

        Raises:
            ValidationError: If value already exists
        """
        # Build query
        query = self.model_class.select().where(self.field == value)

        # Exclude current instance if provided (for updates)
        if self.exclude_instance and self.exclude_instance.id:
            query = query.where(self.model_class.id != self.exclude_instance.id)

        # Check if exists
        existing = query.first()

        if existing:
            field_name = self.field.name
            raise ValidationError(
                field=field_name,
                value=value,
                message=f"An item with {field_name} '{value}' already exists",
                details={"existing_id": str(existing.id), "field": field_name},
            )

        return value


class DateRangeValidator:
    """
    Reusable date range validator.

    This validator ensures that a date falls within a specified range.
    It's useful for validating dates like entry dates, birth dates, etc.

    Attributes:
        min_date: Minimum allowed date (None = no minimum)
        max_date: Maximum allowed date (None = no maximum)
        field_name: Name of the field for error messages

    Examples:
        >>> # Entry date: not in future, minimum 1900
        >>> validator = DateRangeValidator(
        ...     min_date=date(1900, 1, 1),
        ...     max_date=date.today(),
        ...     field_name="entry_date"
        ... )
        >>> validator.validate(date(2020, 1, 15))  # OK
        >>> validator.validate(date(2100, 1, 1))  # Raises ValidationError
    """

    def __init__(self, min_date: Optional[date] = None, max_date: Optional[date] = None, field_name: str = "date"):
        """
        Initialize the date range validator.

        Args:
            min_date: Minimum allowed date (None = no minimum)
            max_date: Maximum allowed date (None = no maximum)
            field_name: Field name for error messages
        """
        self.min_date = min_date
        self.max_date = max_date
        self.field_name = field_name

    def validate(self, value: date) -> date:
        """
        Validate that the date is within the specified range.

        Args:
            value: Date to validate

        Returns:
            The date if valid

        Raises:
            ValidationError: If date is outside range
        """
        if not value:
            raise ValidationError(field=self.field_name, value=value, message=f"{self.field_name} is required")

        if not isinstance(value, date):
            raise ValidationError(
                field=self.field_name, value=value, message=f"{self.field_name} must be a date object"
            )

        # Check minimum
        if self.min_date and value < self.min_date:
            raise ValidationError(
                field=self.field_name,
                value=value,
                message=f"{self.field_name} is too early",
                details={"min_date": self.min_date.isoformat(), "actual_date": value.isoformat()},
            )

        # Check maximum
        if self.max_date and value > self.max_date:
            raise ValidationError(
                field=self.field_name,
                value=value,
                message=f"{self.field_name} is too late",
                details={"max_date": self.max_date.isoformat(), "actual_date": value.isoformat()},
            )

        return value
