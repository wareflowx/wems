"""Tests for input validation framework.

This test module verifies that:
- All validation methods work correctly
- Invalid inputs are rejected with proper error messages
- Edge cases are handled properly
- Malicious inputs are blocked
"""

import pytest
from datetime import datetime
from utils.validation import (
    ValidationError,
    ValidationSeverity,
    InputValidator,
)


class TestSanitizeString:
    """Tests for sanitize_string method."""

    def test_sanitize_basic_string(self):
        """Test sanitizing a normal string."""
        result = InputValidator.sanitize_string("Hello World", 100)
        assert result == "Hello World"

    def test_sanitize_removes_null_bytes(self):
        """Test NULL byte removal."""
        result = InputValidator.sanitize_string("Test\x00String", 100)
        assert result == "TestString"
        assert "\x00" not in result

    def test_sanitize_removes_control_chars(self):
        """Test control character removal."""
        result = InputValidator.sanitize_string("Test\x01\x02String", 100)
        assert "\x01" not in result
        assert "\x02" not in result

    def test_sanitize_keeps_newline_tab(self):
        """Test that \t, \n, \r are preserved."""
        result = InputValidator.sanitize_string("Line1\nLine2\tTab", 100)
        assert "\n" in result
        assert "\t" in result

    def test_sitize_trims_whitespace(self):
        """Test whitespace trimming."""
        result = InputValidator.sanitize_string("  Hello  ", 100)
        assert result == "Hello"

    def test_sanitize_enforces_max_length(self):
        """Test max length enforcement."""
        result = InputValidator.sanitize_string("A" * 200, 50)
        assert len(result) == 50
        assert result == "A" * 50

    def test_sanitize_rejects_non_string(self):
        """Test that non-string types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.sanitize_string(123, 100)
        assert exc_info.value.field == "string"
        assert "string type" in exc_info.value.message


class TestValidateName:
    """Tests for validate_name method."""

    def test_validate_valid_name(self):
        """Test valid name validation."""
        result = InputValidator.validate_name("Jean Dupont", "first_name", 50)
        assert result == "Jean Dupont"

    def test_validate_name_with_accent(self):
        """Test name with accents."""
        result = InputValidator.validate_name("Josée Éric", "first_name", 50)
        assert result == "Josée Éric"

    def test_validate_name_empty_rejected(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_name("", "first_name", 50)
        assert "Cannot be empty" in exc_info.value.message

    def test_validate_name_too_long_rejected(self):
        """Test that too long name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_name("A" * 100, "first_name", 50)
        assert "exceed" in exc_info.value.message

    def test_validate_name_invalid_chars_rejected(self):
        """Test that invalid characters are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_name("Test<script>", "first_name", 50)
        assert "suspicious" in exc_info.value.message

    def test_validate_name_xss_rejected(self):
        """Test that XSS patterns are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_name("<script>alert(1)</script>", "first_name", 50)
        assert "suspicious" in exc_info.value.message

    def test_validate_name_non_string_rejected(self):
        """Test that non-string types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_name(123, "first_name", 50)
        assert "string type" in exc_info.value.message


class TestValidateEmail:
    """Tests for validate_email method."""

    def test_validate_valid_email(self):
        """Test valid email validation."""
        result = InputValidator.validate_email("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_lowercase(self):
        """Test email is normalized to lowercase."""
        result = InputValidator.validate_email("Test@Example.COM")
        assert result == "test@example.com"

    def test_validate_empty_email_allowed(self):
        """Test that empty email is allowed (optional field)."""
        result = InputValidator.validate_email("")
        assert result == ""

    def test_validate_email_invalid_format_rejected(self):
        """Test that invalid email format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("invalid-email")
        assert "Invalid format" in exc_info.value.message

    def test_validate_email_with_double_dots_rejected(self):
        """Test that double dots are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("test..email@example.com")
        assert "Invalid format" in exc_info.value.message

    def test_validate_email_too_long_rejected(self):
        """Test that too long email is rejected."""
        long_email = "a" * 300 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email(long_email)
        assert "exceed" in exc_info.value.message


class TestValidatePhone:
    """Tests for validate_phone method."""

    def test_validate_valid_phone(self):
        """Test valid phone validation."""
        result = InputValidator.validate_phone("0123456789")
        assert result == "0123456789"

    def test_validate_phone_with_formatting(self):
        """Test phone with formatting characters."""
        result = InputValidator.validate_phone("+33 (0)1 23 45 67 89")
        assert "+" in result or len(result.replace("+", "")) >= 10

    def test_validate_empty_phone_allowed(self):
        """Test that empty phone is allowed (optional field)."""
        result = InputValidator.validate_phone("")
        assert result == ""

    def test_validate_phone_too_short_rejected(self):
        """Test that too short phone is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_phone("123")
        assert "Invalid length" in exc_info.value.message

    def test_validate_phone_too_long_rejected(self):
        """Test that too long phone is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_phone("0" * 20)
        assert "Invalid length" in exc_info.value.message


class TestValidateDate:
    """Tests for validate_date method."""

    def test_validate_datetime_object(self):
        """Test validation of datetime object."""
        date = datetime(2024, 1, 15)
        result = InputValidator.validate_date(date, "test_date")
        assert result == date

    def test_validate_date_string_yyyy_mm_dd(self):
        """Test validation of YYYY-MM-DD format."""
        result = InputValidator.validate_date("2024-01-15", "test_date")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_validate_date_string_dd_mm_yyyy(self):
        """Test validation of DD/MM/YYYY format."""
        result = InputValidator.validate_date("15/01/2024", "test_date")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_validate_date_future_rejected(self):
        """Test that future dates are rejected by default."""
        future_date = datetime(2050, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_date(future_date, "test_date", allow_future=False)
        assert "future" in exc_info.value.message

    def test_validate_date_too_old_rejected(self):
        """Test that dates before 1900 are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_date("1800-01-01", "test_date")
        assert "Year out of range" in exc_info.value.message

    def test_validate_date_invalid_format_rejected(self):
        """Test that invalid date format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_date("invalid-date", "test_date")
        assert "Invalid date format" in exc_info.value.message

    def test_validate_date_future_allowed(self):
        """Test that future dates can be allowed."""
        future_date = datetime(2025, 1, 1)
        result = InputValidator.validate_date(future_date, "test_date", allow_future=True)
        assert result.year == 2025


class TestValidateStatus:
    """Tests for validate_status method."""

    def test_validate_valid_status(self):
        """Test valid status validation."""
        result = InputValidator.validate_status("active")
        assert result == "active"

    def test_validate_status_invalid_rejected(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_status("invalid_status")
        assert "Must be one of" in exc_info.value.message


class TestValidateEnum:
    """Tests for validate_enum method."""

    def test_validate_enum_valid_value(self):
        """Test valid enum value."""
        result = InputValidator.validate_enum("CDI", "contract_type", ["CDI", "CDD", "Intérim"])
        assert result == "CDI"

    def test_validate_enum_invalid_rejected(self):
        """Test that invalid enum value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_enum("invalid", "test", ["A", "B", "C"])
        assert "Must be one of" in exc_info.value.message


class TestValidateEmployeeData:
    """Tests for validate_employee_data method."""

    def test_validate_complete_valid_data(self):
        """Test validation of complete valid employee data."""
        data = {
            'external_id': 'WMS-001',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean.dupont@example.com',
            'phone': '0123456789',
            'entry_date': '2024-01-15',
            'current_status': 'active',
            'workspace': 'Zone A',
            'role': 'Cariste',
            'contract_type': 'CDI',
        }
        result = InputValidator.validate_employee_data(data)
        assert result['first_name'] == 'Jean'
        assert result['last_name'] == 'Dupont'
        assert result['email'] == 'jean.dupont@example.com'

    def test_validate_employee_data_missing_optional(self):
        """Test that optional fields can be omitted."""
        data = {
            'external_id': 'WMS-002',
            'first_name': 'Marie',
            'last_name': 'Martin',
        }
        result = InputValidator.validate_employee_data(data)
        assert result['first_name'] == 'Marie'
        assert 'email' not in result
        assert 'phone' not in result

    def test_validate_employee_data_invalid_email_raises(self):
        """Test that invalid email raises ValidationError."""
        data = {
            'external_id': 'WMS-003',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid-email',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_employee_data(data)

    def test_validate_employee_data_invalid_status_raises(self):
        """Test that invalid status raises ValidationError."""
        data = {
            'external_id': 'WMS-004',
            'first_name': 'Test',
            'last_name': 'User',
            'current_status': 'invalid_status',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_employee_data(data)


class TestValidateCACESKind:
    """Tests for validate_caces_kind method."""

    def test_validate_valid_caces_kind(self):
        """Test valid CACES kind validation."""
        result = InputValidator.validate_caces_kind("R489-1A")
        assert result == "R489-1A"

    def test_validate_caces_kind_invalid_rejected(self):
        """Test that invalid CACES kind is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_caces_kind("INVALID")
        assert "Must be one of" in exc_info.value.message

    def test_validate_caces_kind_non_string_rejected(self):
        """Test that non-string types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_caces_kind(123)
        assert "string type" in exc_info.value.message


class TestValidateVisitType:
    """Tests for validate_visit_type method."""

    def test_validate_valid_visit_type(self):
        """Test valid visit type validation."""
        result = InputValidator.validate_visit_type("initial")
        assert result == "initial"

    def test_validate_visit_type_invalid_rejected(self):
        """Test that invalid visit type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_visit_type("invalid_type")
        assert "Must be one of" in exc_info.value.message


class TestValidateVisitResult:
    """Tests for validate_visit_result method."""

    def test_validate_valid_visit_result(self):
        """Test valid visit result validation."""
        result = InputValidator.validate_visit_result("fit")
        assert result == "fit"

    def test_validate_visit_result_invalid_rejected(self):
        """Test that invalid visit result is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_visit_result("invalid_result")
        assert "Must be one of" in exc_info.value.message


class TestValidateCACESData:
    """Tests for validate_caces_data method."""

    def test_validate_complete_caces_data(self):
        """Test validation of complete valid CACES data."""
        data = {
            'kind': 'R489-1A',
            'completion_date': '2024-01-15',
        }
        result = InputValidator.validate_caces_data(data)
        assert result['kind'] == 'R489-1A'

    def test_validate_caces_data_invalid_kind_raises(self):
        """Test that invalid CACES kind raises ValidationError."""
        data = {
            'kind': 'INVALID',
            'completion_date': '2024-01-15',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_caces_data(data)

    def test_validate_caces_data_missing_date_raises(self):
        """Test that missing completion date raises ValidationError."""
        data = {
            'kind': 'R489-1A',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_caces_data(data)


class TestValidateMedicalVisitData:
    """Tests for validate_medical_visit_data method."""

    def test_validate_complete_medical_visit_data(self):
        """Test validation of complete valid medical visit data."""
        data = {
            'visit_type': 'initial',
            'visit_date': '2024-01-15',
            'result': 'fit',
        }
        result = InputValidator.validate_medical_visit_data(data)
        assert result['visit_type'] == 'initial'
        assert result['result'] == 'fit'

    def test_validate_medical_visit_data_invalid_type_raises(self):
        """Test that invalid visit type raises ValidationError."""
        data = {
            'visit_type': 'invalid_type',
            'visit_date': '2024-01-15',
            'result': 'fit',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_medical_visit_data(data)

    def test_validate_medical_visit_data_missing_result_raises(self):
        """Test that missing result raises ValidationError."""
        data = {
            'visit_type': 'initial',
            'visit_date': '2024-01-15',
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_medical_visit_data(data)
