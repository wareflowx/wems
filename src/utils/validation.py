"""Input validation and sanitization framework.

This module provides comprehensive input validation to protect against:
- Injection attacks (SQL, XSS, command injection)
- Buffer overflow attacks
- Data corruption
- Unicode attacks
- Format violations
"""

import re
import unicodedata
from typing import Any, Optional, Tuple, List
from datetime import datetime
from enum import Enum


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class InputValidator:
    """Comprehensive input validation framework."""

    # Character sets (simplified - \p{L} not supported in Python regex)
    # We'll validate using Unicode categories instead in the methods
    ALLOWED_EMAIL_CHARS = re.compile(r"^[a-zA-Z0-9._%+\-@]+$")
    # Note: Phone validation is done in validate_phone() method, not with regex

    # Length limits
    MAX_LENGTH_FIRST_NAME = 50
    MAX_LENGTH_LAST_NAME = 50
    MAX_LENGTH_EMAIL = 255
    MAX_LENGTH_PHONE = 20
    MAX_LENGTH_COMMENT = 2000
    MAX_LENGTH_EXTERNAL_ID = 50
    MAX_LENGTH_WORKSPACE = 50
    MAX_LENGTH_ROLE = 100
    MAX_LENGTH_CONTRACT_TYPE = 50

    # Allowed values
    ALLOWED_STATUSES = ['active', 'inactive']
    ALLOWED_CONTRACT_TYPES = ['CDI', 'CDD', 'Intérim', 'Alternance', 'Stage']
    ALLOWED_CACES_KINDS = ['R489-1A', 'R489-1B', 'R489-3', 'R489-4', 'R489-5']
    ALLOWED_VISIT_TYPES = ['initial', 'periodic', 'recovery']
    ALLOWED_VISIT_RESULTS = ['fit', 'unfit', 'fit_with_restrictions']

    # Date ranges
    MIN_YEAR = 1900
    MAX_YEAR = 2100

    @staticmethod
    def sanitize_string(value: str, max_length: int) -> str:
        """
        Sanitize string input.

        - Remove NULL bytes
        - Remove control characters (except newline, tab)
        - Normalize Unicode (NFC - canonical composition)
        - Trim whitespace
        - Enforce max length

        Args:
            value: Input string
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValidationError("string", "Must be string type", value)

        # Remove NULL bytes
        value = value.replace('\x00', '')

        # Normalize Unicode to NFC form
        value = unicodedata.normalize('NFC', value)

        # Remove control characters (except \t, \n, \r)
        value = ''.join(
            char for char in value
            if char == '\t' or char == '\n' or char == '\r'
            or not unicodedata.category(char).startswith('C')
        )

        # Trim whitespace
        value = value.strip()

        # Enforce max length
        if len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def validate_name(value: str, field_name: str = "name", max_length: int = 50) -> str:
        """
        Validate person name.

        Args:
            value: Name to validate
            field_name: Field name for error messages
            max_length: Maximum allowed length

        Returns:
            Sanitized name

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be string type", value)

        # Check for suspicious patterns FIRST (before sanitization)
        if re.search(r'<script|javascript:|onerror=|onload=', value, re.IGNORECASE):
            raise ValidationError(field_name, "Contains suspicious content", value)

        # Length check BEFORE sanitization
        if len(value) == 0:
            raise ValidationError(field_name, "Cannot be empty")
        if len(value) > max_length:
            raise ValidationError(field_name, f"Cannot exceed {max_length} characters")

        # Sanitize
        value = InputValidator.sanitize_string(value, max_length)

        # Character validation (allow Unicode letters, marks, hyphen, apostrophe, space)
        # Use Unicode categories: L (Letter), M (Mark)
        if not all(
            unicodedata.category(char).startswith(('L', 'M', 'Zs'))  # Letter, Mark, space
            or char in "'\\-"
            for char in value
        ):
            raise ValidationError(field_name, "Contains invalid characters", value)

        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate email address.

        Args:
            value: Email to validate

        Returns:
            Sanitized email

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError("email", "Must be string type", value)

        # Allow empty email (optional field)
        value = value.strip()
        if value == "":
            return ""

        # Length check BEFORE sanitization
        if len(value) > InputValidator.MAX_LENGTH_EMAIL:
            raise ValidationError("email", f"Cannot exceed {InputValidator.MAX_LENGTH_EMAIL} characters")

        # Sanitize
        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_EMAIL)

        # Format validation (RFC 5322 basic)
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(value):
            raise ValidationError("email", "Invalid format", value)

        # Check for suspicious patterns
        if '..' in value or value.startswith('.') or value.endswith('.'):
            raise ValidationError("email", "Invalid format", value)

        return value.lower()  # Normalize to lowercase

    @staticmethod
    def validate_phone(value: str) -> str:
        """
        Validate phone number.

        Args:
            value: Phone number to validate

        Returns:
            Sanitized phone number

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError("phone", "Must be string type", value)

        # Allow empty phone (optional field)
        value = value.strip()
        if value == "":
            return ""

        # Sanitize
        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_PHONE)

        # Remove common formatting
        digits_only = re.sub(r'[^\d+]', '', value)

        # Length check (reasonable phone number length)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValidationError("phone", "Invalid length (must be 10-15 digits)", value)

        return value

    @staticmethod
    def validate_date(value: Any, field_name: str = "date", allow_future: bool = False) -> datetime:
        """
        Validate date input.

        Args:
            value: Date to validate (string or datetime)
            field_name: Field name for error messages
            allow_future: Whether future dates are allowed

        Returns:
            Datetime object

        Raises:
            ValidationError: If validation fails
        """
        # If already datetime, validate range
        if isinstance(value, datetime):
            if value.year < InputValidator.MIN_YEAR or value.year > InputValidator.MAX_YEAR:
                raise ValidationError(field_name, f"Year out of range ({InputValidator.MIN_YEAR}-{InputValidator.MAX_YEAR})", value)

            # Cannot be in future (unless allowed)
            if not allow_future and value > datetime.now():
                raise ValidationError(field_name, "Date cannot be in future", value)

            return value

        # If string, parse
        if isinstance(value, str):
            value = value.strip()

            try:
                # Try common formats
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(field_name, f"Invalid date format (use YYYY-MM-DD)", value)

                # Validate range
                if parsed_date.year < InputValidator.MIN_YEAR or parsed_date.year > InputValidator.MAX_YEAR:
                    raise ValidationError(field_name, f"Year out of range ({InputValidator.MIN_YEAR}-{InputValidator.MAX_YEAR})", value)

                # Cannot be in future (unless allowed)
                if not allow_future and parsed_date > datetime.now():
                    raise ValidationError(field_name, "Date cannot be in future", value)

                return parsed_date

            except Exception as e:
                raise ValidationError(field_name, f"Invalid date: {e}", value) from e

        raise ValidationError(field_name, "Must be date or string", value)

    @staticmethod
    def validate_status(value: str) -> str:
        """Validate employee status."""
        if value not in InputValidator.ALLOWED_STATUSES:
            raise ValidationError("current_status", f"Must be one of: {InputValidator.ALLOWED_STATUSES}", value)
        return value

    @staticmethod
    def validate_enum(value: str, field_name: str, allowed_values: List[str]) -> str:
        """
        Validate enum/choice field.

        Args:
            value: Value to validate
            field_name: Field name for errors
            allowed_values: List of allowed values

        Returns:
            Validated value
        """
        if value not in allowed_values:
            raise ValidationError(field_name, f"Must be one of: {allowed_values}", value)
        return value

    @staticmethod
    def validate_comment(value: str) -> str:
        """Validate comment field."""
        if not isinstance(value, str):
            raise ValidationError("comment", "Must be string type", value)

        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_COMMENT)

        # Allow most characters in comments (free text)
        # But remove control characters (already done in sanitize_string)
        return value

    @staticmethod
    def validate_external_id(value: str) -> str:
        """Validate external ID."""
        if not isinstance(value, str):
            raise ValidationError("external_id", "Must be string type", value)

        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_EXTERNAL_ID)

        if len(value) == 0:
            raise ValidationError("external_id", "Cannot be empty")

        # Alphanumeric, underscore, hyphen only
        if not re.match(r'^[a-zA-Z0-9_\\-]+$', value):
            raise ValidationError("external_id", "Invalid format (alphanumeric, _, - only)", value)

        return value

    @classmethod
    def validate_employee_data(cls, data: dict) -> dict:
        """
        Validate all employee data.

        Args:
            data: Dictionary of employee data

        Returns:
            Sanitized and validated data

        Raises:
            ValidationError: If any validation fails
        """
        validated = {}

        try:
            # Required fields
            validated['external_id'] = cls.validate_external_id(data.get('external_id', ''))
            validated['first_name'] = cls.validate_name(data.get('first_name', ''), 'first_name', cls.MAX_LENGTH_FIRST_NAME)
            validated['last_name'] = cls.validate_name(data.get('last_name', ''), 'last_name', cls.MAX_LENGTH_LAST_NAME)

            # Optional fields
            email = data.get('email', '')
            if email:
                validated['email'] = cls.validate_email(email)

            phone = data.get('phone', '')
            if phone:
                validated['phone'] = cls.validate_phone(phone)

            entry_date = data.get('entry_date')
            if entry_date:
                validated['entry_date'] = cls.validate_date(entry_date, 'entry_date')

            # Enums
            current_status = data.get('current_status', 'active')
            validated['current_status'] = cls.validate_status(current_status)

            # Optional text fields
            workspace = data.get('workspace', '')
            if workspace:
                validated['workspace'] = cls.sanitize_string(workspace, cls.MAX_LENGTH_WORKSPACE)

            role = data.get('role', '')
            if role:
                validated['role'] = cls.sanitize_string(role, cls.MAX_LENGTH_ROLE)

            contract_type = data.get('contract_type', '')
            if contract_type:
                validated['contract_type'] = cls.validate_enum(
                    contract_type, 'contract_type', cls.ALLOWED_CONTRACT_TYPES
                )

            comment = data.get('comment', '')
            if comment:
                validated['comment'] = cls.validate_comment(comment)

            return validated

        except ValidationError as e:
            # Re-raise with context
            raise e

    @staticmethod
    def validate_caces_kind(value: str) -> str:
        """
        Validate CACES certification kind.

        Args:
            value: CACES kind (e.g., 'R489-1A')

        Returns:
            Validated CACES kind

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("caces_kind", "Must be string type", value)

        value = value.strip()
        if value not in InputValidator.ALLOWED_CACES_KINDS:
            raise ValidationError("caces_kind", f"Must be one of: {InputValidator.ALLOWED_CACES_KINDS}", value)

        return value

    @staticmethod
    def validate_visit_type(value: str) -> str:
        """
        Validate medical visit type.

        Args:
            value: Visit type ('initial', 'periodic', 'recovery')

        Returns:
            Validated visit type

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("visit_type", "Must be string type", value)

        value = value.strip()
        if value not in InputValidator.ALLOWED_VISIT_TYPES:
            raise ValidationError("visit_type", f"Must be one of: {InputValidator.ALLOWED_VISIT_TYPES}", value)

        return value

    @staticmethod
    def validate_visit_result(value: str) -> str:
        """
        Validate medical visit result.

        Args:
            value: Visit result ('fit', 'unfit', 'fit_with_restrictions')

        Returns:
            Validated visit result

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("visit_result", "Must be string type", value)

        value = value.strip()
        if value not in InputValidator.ALLOWED_VISIT_RESULTS:
            raise ValidationError("visit_result", f"Must be one of: {InputValidator.ALLOWED_VISIT_RESULTS}", value)

        return value

    @classmethod
    def validate_caces_data(cls, data: dict) -> dict:
        """
        Validate CACES certification data.

        Args:
            data: Dictionary of CACES data

        Returns:
            Sanitized and validated data

        Raises:
            ValidationError: If any validation fails
        """
        validated = {}

        try:
            # Required fields
            validated['kind'] = cls.validate_caces_kind(data.get('kind', ''))

            completion_date = data.get('completion_date')
            if completion_date:
                validated['completion_date'] = cls.validate_date(completion_date, 'completion_date')
            else:
                raise ValidationError('completion_date', 'Cannot be empty')

            # Optional fields
            document_path = data.get('document_path', '')
            if document_path:
                validated['document_path'] = cls.sanitize_string(document_path, 500)

            return validated

        except ValidationError as e:
            raise e

    @classmethod
    def validate_medical_visit_data(cls, data: dict) -> dict:
        """
        Validate medical visit data.

        Args:
            data: Dictionary of medical visit data

        Returns:
            Sanitized and validated data

        Raises:
            ValidationError: If any validation fails
        """
        validated = {}

        try:
            # Required fields
            validated['visit_type'] = cls.validate_visit_type(data.get('visit_type', ''))

            visit_date = data.get('visit_date')
            if visit_date:
                validated['visit_date'] = cls.validate_date(visit_date, 'visit_date')
            else:
                raise ValidationError('visit_date', 'Cannot be empty')

            validated['result'] = cls.validate_visit_result(data.get('result', ''))

            # Optional fields
            document_path = data.get('document_path', '')
            if document_path:
                validated['document_path'] = cls.sanitize_string(document_path, 500)

            return validated

        except ValidationError as e:
            raise e
