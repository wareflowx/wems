"""Tests for utils/validation.py module."""

import pytest
from datetime import date, datetime
from utils.validation import ValidationError, ValidationSeverity, InputValidator


# =============================================================================
# TESTS: ValidationError
# =============================================================================

class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_creation(self):
        """Should create error with all attributes."""
        error = ValidationError(field="test_field", message="Test error", value="test_value")

        assert error.field == "test_field"
        assert error.message == "Test error"
        assert error.value == "test_value"

    def test_validation_error_str(self):
        """Should format error message correctly."""
        error = ValidationError(field="email", message="Invalid format", value="test@test")

        error_str = str(error)
        assert "email" in error_str
        assert "Invalid format" in error_str

    def test_validation_error_without_value(self):
        """Should handle error without value."""
        error = ValidationError(field="name", message="Required")

        assert error.field == "name"
        assert error.value is None


# =============================================================================
# TESTS: ValidationSeverity
# =============================================================================

class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_severity_values(self):
        """Should have correct severity values."""
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.CRITICAL.value == "critical"


# =============================================================================
# TESTS: InputValidator.sanitize_string
# =============================================================================

class TestSanitizeString:
    """Tests for sanitize_string method."""

    def test_sanitize_normal_string(self):
        """Should pass through normal strings."""
        result = InputValidator.sanitize_string("Hello World", 100)
        assert result == "Hello World"

    def test_sanitize_removes_null_bytes(self):
        """Should remove NULL bytes."""
        result = InputValidator.sanitize_string("Test\x00String", 100)
        assert result == "TestString"

    def test_sitize_removes_control_chars(self):
        """Should remove control characters except tab/newline."""
        # Control characters should be removed
        result = InputValidator.sanitize_string("Test\x01\x02String", 100)
        assert result == "TestString"

    def test_sanitize_preserves_tab_newline(self):
        """Should preserve tab and newline."""
        result = InputValidator.sanitize_string("Line1\nLine2\tTabbed", 100)
        assert "\n" in result
        assert "\t" in result

    def test_sanitize_trims_whitespace(self):
        """Should trim leading/trailing whitespace."""
        result = InputValidator.sanitize_string("  Hello  ", 100)
        assert result == "Hello"

    def test_sanitize_enforces_max_length(self):
        """Should truncate to max length."""
        result = InputValidator.sanitize_string("A" * 100, 50)
        assert len(result) == 50
        assert result == "A" * 50

    def test_sitize_unicode_normalization(self):
        """Should normalize Unicode to NFC form."""
        # Composed vs decomposed forms
        result = InputValidator.sanitize_string("café", 100)
        assert len(result) == 4

    def test_sanitize_non_string_raises_error(self):
        """Should raise ValidationError for non-string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.sanitize_string(123, 100)

        assert exc.value.field == "string"
        assert "Must be string type" in exc.value.message


# =============================================================================
# TESTS: InputValidator.validate_name
# =============================================================================

class TestValidateName:
    """Tests for validate_name method."""

    def test_valid_name(self):
        """Should accept valid names."""
        result = InputValidator.validate_name("John Doe", "name", 50)
        assert result == "John Doe"

    def test_name_with_hyphen(self):
        """Should accept names with hyphens."""
        result = InputValidator.validate_name("Jean-Pierre", "name", 50)
        assert "Jean-Pierre" in result

    def test_name_with_apostrophe(self):
        """Should accept names with apostrophes."""
        result = InputValidator.validate_name("O'Connor", "name", 50)
        assert "O'Connor" in result

    def test_name_with_unicode_letters(self):
        """Should accept Unicode letters."""
        result = InputValidator.validate_name("José", "name", 50)
        assert "José" in result

    def test_empty_name_raises_error(self):
        """Should raise error for empty name."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_name("", "name", 50)

        assert exc.value.field == "name"
        assert "Cannot be empty" in exc.value.message

    def test_name_too_long_raises_error(self):
        """Should raise error for name too long."""
        long_name = "A" * 51
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_name(long_name, "name", 50)

        assert exc.value.field == "name"
        assert "Cannot exceed" in exc.value.message

    def test_name_with_script_injection(self):
        """Should reject script injection attempts."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_name("<script>alert('xss')</script>", "name", 50)

        assert exc.value.field == "name"
        assert "suspicious" in exc.value.message.lower()

    def test_name_with_javascript_injection(self):
        """Should reject javascript: injection."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_name("javascript:alert('xss')", "name", 50)

        assert "suspicious" in exc.value.message.lower()

    def test_non_string_name_raises_error(self):
        """Should raise error for non-string name."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_name(123, "name", 50)

        assert exc.value.field == "name"


# =============================================================================
# TESTS: InputValidator.validate_email
# =============================================================================

class TestValidateEmail:
    """Tests for validate_email method."""

    def test_valid_email(self):
        """Should accept valid email."""
        result = InputValidator.validate_email("test@example.com")
        assert result == "test@example.com"

    def test_email_normalized_to_lowercase(self):
        """Should normalize email to lowercase."""
        result = InputValidator.validate_email("TEST@EXAMPLE.COM")
        assert result == "test@example.com"

    def test_empty_email_allowed(self):
        """Should allow empty email (optional field)."""
        result = InputValidator.validate_email("")
        assert result == ""

    def test_whitespace_email_allowed(self):
        """Should allow whitespace-only email."""
        result = InputValidator.validate_email("   ")
        assert result == ""

    def test_email_too_long_raises_error(self):
        """Should reject email exceeding max length."""
        long_email = "a" * 256 + "@example.com"
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_email(long_email)

        assert exc.value.field == "email"
        assert "Cannot exceed" in exc.value.message

    def test_invalid_email_format(self):
        """Should reject invalid email format."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_email("not-an-email")

        assert exc.value.field == "email"

    def test_non_string_email_raises_error(self):
        """Should raise error for non-string email."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_email(123)

        assert exc.value.field == "email"


# =============================================================================
# TESTS: InputValidator.validate_phone
# =============================================================================

class TestValidatePhone:
    """Tests for validate_phone method."""

    def test_valid_phone(self):
        """Should accept valid phone number."""
        result = InputValidator.validate_phone("0123456789")
        assert result == "0123456789"

    def test_phone_with_formatting(self):
        """Should accept phone with common formatting."""
        result = InputValidator.validate_phone("01-23-45-67-89")
        assert "01" in result  # Should preserve formatting

    def test_phone_with_spaces(self):
        """Should accept phone with spaces."""
        result = InputValidator.validate_phone("01 23 45 67 89")
        assert "01" in result

    def test_phone_with_plus_sign(self):
        """Should accept international number with +."""
        result = InputValidator.validate_phone("+33123456789")
        assert "+" in result

    def test_empty_phone_allowed(self):
        """Should allow empty phone (optional field)."""
        result = InputValidator.validate_phone("")
        assert result == ""

    def test_phone_too_short_raises_error(self):
        """Should reject phone with less than 10 digits."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_phone("123456789")

        assert exc.value.field == "phone"
        assert "Invalid length" in exc.value.message

    def test_phone_too_long_raises_error(self):
        """Should reject phone with more than 15 digits."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_phone("1" * 16)

        assert exc.value.field == "phone"
        assert "Invalid length" in exc.value.message

    def test_non_string_phone_raises_error(self):
        """Should raise error for non-string phone."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_phone(123)

        assert exc.value.field == "phone"


# =============================================================================
# TESTS: InputValidator.validate_date
# =============================================================================

class TestValidateDate:
    """Tests for validate_date method."""

    def test_valid_date_object(self):
        """Should accept valid date object."""
        result = InputValidator.validate_date(date(2020, 1, 15))
        assert result == date(2020, 1, 15)

    def test_datetime_converted_to_date(self):
        """Should convert datetime to date."""
        dt = datetime(2020, 1, 15, 12, 30, 0)
        result = InputValidator.validate_date(dt)
        assert result == date(2020, 1, 15)

    def test_date_string_yyyy_mm_dd(self):
        """Should parse YYYY-MM-DD format."""
        result = InputValidator.validate_date("2020-01-15")
        assert result == date(2020, 1, 15)

    def test_date_string_dd_mm_yyyy(self):
        """Should parse DD/MM/YYYY format."""
        result = InputValidator.validate_date("15/01/2020")
        assert result == date(2020, 1, 15)

    def test_date_string_yyyy_mm_dd_slashes(self):
        """Should parse YYYY/MM/DD format."""
        result = InputValidator.validate_date("2020/01/15")
        assert result == date(2020, 1, 15)

    def test_future_date_rejected_by_default(self):
        """Should reject future dates by default."""
        future_date = date.today().replace(year=date.today().year + 1)
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date(future_date)

        assert "future" in exc.value.message.lower()

    def test_future_date_allowed_when_flag_set(self):
        """Should allow future dates when flag is set."""
        future_date = date.today().replace(year=date.today().year + 1)
        result = InputValidator.validate_date(future_date, allow_future=True)
        assert result == future_date

    def test_year_too_old_raises_error(self):
        """Should reject years before MIN_YEAR."""
        old_date = date(1800, 1, 1)
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date(old_date)

        assert "out of range" in exc.value.message

    def test_year_too_future_raises_error(self):
        """Should reject years after MAX_YEAR."""
        future_date = date(2200, 1, 1)
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date(future_date, allow_future=True)

        assert "out of range" in exc.value.message

    def test_invalid_date_string_raises_error(self):
        """Should reject invalid date string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date("invalid-date")

        assert exc.value.field == "date"

    def test_unsupported_type_raises_error(self):
        """Should reject unsupported types."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date(123)

        assert exc.value.field == "date"


# =============================================================================
# TESTS: InputValidator.validate_status
# =============================================================================

class TestValidateStatus:
    """Tests for validate_status method."""

    def test_valid_active_status(self):
        """Should accept 'active' status."""
        result = InputValidator.validate_status("active")
        assert result == "active"

    def test_valid_inactive_status(self):
        """Should accept 'inactive' status."""
        result = InputValidator.validate_status("inactive")
        assert result == "inactive"

    def test_invalid_status_raises_error(self):
        """Should reject invalid status."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_status("unknown")

        assert exc.value.field == "current_status"
        assert "Must be one of" in exc.value.message


# =============================================================================
# TESTS: InputValidator.validate_enum
# =============================================================================

class TestValidateEnum:
    """Tests for validate_enum method."""

    def test_valid_enum_value(self):
        """Should accept valid enum value."""
        result = InputValidator.validate_enum("CDI", "contract_type", ["CDI", "CDD"])
        assert result == "CDI"

    def test_invalid_enum_raises_error(self):
        """Should reject invalid enum value."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_enum("Invalid", "field", ["A", "B"])

        assert exc.value.field == "field"
        assert "Must be one of" in exc.value.message


# =============================================================================
# TESTS: InputValidator.validate_comment
# =============================================================================

class TestValidateComment:
    """Tests for validate_comment method."""

    def test_valid_comment(self):
        """Should accept valid comment."""
        result = InputValidator.validate_comment("This is a comment")
        assert result == "This is a comment"

    def test_comment_with_newlines(self):
        """Should preserve newlines in comment."""
        result = InputValidator.validate_comment("Line1\nLine2")
        assert "\n" in result

    def test_long_comment_truncated(self):
        """Should truncate long comments."""
        long_comment = "A" * 3000
        result = InputValidator.validate_comment(long_comment)
        assert len(result) <= 2000

    def test_non_string_comment_raises_error(self):
        """Should raise error for non-string comment."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_comment(123)

        assert exc.value.field == "comment"


# =============================================================================
# TESTS: InputValidator.validate_external_id
# =============================================================================

class TestValidateExternalID:
    """Tests for validate_external_id method."""

    def test_valid_external_id(self):
        """Should accept valid external ID."""
        result = InputValidator.validate_external_id("WMS-001")
        assert result == "WMS-001"

    def test_external_id_with_underscore(self):
        """Should accept underscore in ID."""
        result = InputValidator.validate_external_id("EMP_001")
        assert result == "EMP_001"

    def test_external_id_with_hyphen(self):
        """Should accept hyphen in ID."""
        result = InputValidator.validate_external_id("R489-1A")
        assert result == "R489-1A"

    def test_empty_external_id_raises_error(self):
        """Should reject empty external ID."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_external_id("")

        assert exc.value.field == "external_id"
        assert "Cannot be empty" in exc.value.message

    def test_external_id_with_special_chars_raises_error(self):
        """Should reject special characters."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_external_id("ID@001")

        assert exc.value.field == "external_id"
        assert "Invalid format" in exc.value.message

    def test_non_string_external_id_raises_error(self):
        """Should raise error for non-string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_external_id(123)

        assert exc.value.field == "external_id"


# =============================================================================
# TESTS: InputValidator.validate_employee_data
# =============================================================================

class TestValidateEmployeeData:
    """Tests for validate_employee_data method."""

    def test_valid_employee_data(self):
        """Should validate complete employee data."""
        data = {
            'external_id': 'WMS-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '0123456789',
            'entry_date': date(2020, 1, 15),
            'current_status': 'active',
            'workspace': 'Quai',
            'role': 'Cariste',
            'contract_type': 'CDI'
        }

        result = InputValidator.validate_employee_data(data)

        assert result['external_id'] == 'WMS-001'
        assert result['first_name'] == 'John'
        assert result['last_name'] == 'Doe'
        assert result['email'] == 'john@example.com'

    def test_employee_data_without_optional_fields(self):
        """Should validate employee data with only required fields."""
        data = {
            'external_id': 'WMS-002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'current_status': 'active'
        }

        result = InputValidator.validate_employee_data(data)

        assert result['external_id'] == 'WMS-002'
        assert 'email' not in result  # Optional field not provided

    def test_employee_data_with_invalid_email_raises_error(self):
        """Should raise error for invalid email."""
        data = {
            'external_id': 'WMS-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email'
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_employee_data(data)

    def test_employee_data_with_invalid_status_raises_error(self):
        """Should raise error for invalid status."""
        data = {
            'external_id': 'WMS-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'current_status': 'invalid'
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_employee_data(data)

    def test_employee_data_with_comment(self):
        """Should handle comment field."""
        data = {
            'external_id': 'WMS-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'comment': 'This is a test comment'
        }

        result = InputValidator.validate_employee_data(data)
        assert result['comment'] == 'This is a test comment'


# =============================================================================
# TESTS: InputValidator.validate_caces_kind
# =============================================================================

class TestValidateCacesKind:
    """Tests for validate_caces_kind method."""

    def test_valid_caces_kind(self):
        """Should accept valid CACES kinds."""
        for kind in ['R489-1A', 'R489-1B', 'R489-3', 'R489-4', 'R489-5']:
            result = InputValidator.validate_caces_kind(kind)
            assert result == kind

    def test_invalid_caces_kind_raises_error(self):
        """Should reject invalid CACES kind."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_caces_kind("R489-2")

        assert exc.value.field == "caces_kind"
        assert "Must be one of" in exc.value.message

    def test_non_string_caces_kind_raises_error(self):
        """Should raise error for non-string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_caces_kind(123)

        assert exc.value.field == "caces_kind"


# =============================================================================
# TESTS: InputValidator.validate_visit_type
# =============================================================================

class TestValidateVisitType:
    """Tests for validate_visit_type method."""

    def test_valid_visit_types(self):
        """Should accept valid visit types."""
        for visit_type in ['initial', 'periodic', 'recovery']:
            result = InputValidator.validate_visit_type(visit_type)
            assert result == visit_type

    def test_invalid_visit_type_raises_error(self):
        """Should reject invalid visit type."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_visit_type("invalid")

        assert exc.value.field == "visit_type"

    def test_non_string_visit_type_raises_error(self):
        """Should raise error for non-string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_visit_type(123)

        assert exc.value.field == "visit_type"


# =============================================================================
# TESTS: InputValidator.validate_visit_result
# =============================================================================

class TestValidateVisitResult:
    """Tests for validate_visit_result method."""

    def test_valid_visit_results(self):
        """Should accept valid visit results."""
        for result in ['fit', 'unfit', 'fit_with_restrictions']:
            res = InputValidator.validate_visit_result(result)
            assert res == result

    def test_invalid_visit_result_raises_error(self):
        """Should reject invalid visit result."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_visit_result("invalid")

        assert exc.value.field == "visit_result"

    def test_non_string_visit_result_raises_error(self):
        """Should raise error for non-string."""
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_visit_result(123)

        assert exc.value.field == "visit_result"


# =============================================================================
# TESTS: InputValidator.validate_caces_data
# =============================================================================

class TestValidateCacesData:
    """Tests for validate_caces_data method."""

    def test_valid_caces_data(self):
        """Should validate complete CACES data."""
        data = {
            'kind': 'R489-1A',
            'completion_date': date(2020, 1, 15),
            'document_path': '/path/to/caces.pdf'
        }

        result = InputValidator.validate_caces_data(data)

        assert result['kind'] == 'R489-1A'
        assert result['completion_date'] == date(2020, 1, 15)
        assert result['document_path'] == '/path/to/caces.pdf'

    def test_caces_data_without_optional_fields(self):
        """Should validate with only required fields."""
        data = {
            'kind': 'R489-3',
            'completion_date': '2020-01-15'
        }

        result = InputValidator.validate_caces_data(data)

        assert result['kind'] == 'R489-3'
        assert result['completion_date'] == date(2020, 1, 15)

    def test_caces_data_missing_kind_raises_error(self):
        """Should raise error for missing kind."""
        data = {
            'completion_date': date(2020, 1, 15)
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_caces_data(data)

    def test_caces_data_missing_completion_date_raises_error(self):
        """Should raise error for missing completion date."""
        data = {
            'kind': 'R489-1A'
        }

        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_caces_data(data)

        assert exc.value.field == "completion_date"

    def test_caces_data_invalid_kind_raises_error(self):
        """Should raise error for invalid kind."""
        data = {
            'kind': 'INVALID',
            'completion_date': date(2020, 1, 15)
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_caces_data(data)


# =============================================================================
# TESTS: InputValidator.validate_medical_visit_data
# =============================================================================

class TestValidateMedicalVisitData:
    """Tests for validate_medical_visit_data method."""

    def test_valid_medical_visit_data(self):
        """Should validate complete medical visit data."""
        data = {
            'visit_type': 'periodic',
            'visit_date': date(2020, 1, 15),
            'result': 'fit',
            'document_path': '/path/to/visit.pdf'
        }

        result = InputValidator.validate_medical_visit_data(data)

        assert result['visit_type'] == 'periodic'
        assert result['visit_date'] == date(2020, 1, 15)
        assert result['result'] == 'fit'

    def test_medical_visit_data_without_optional_fields(self):
        """Should validate with only required fields."""
        data = {
            'visit_type': 'initial',
            'visit_date': '2020-01-15',
            'result': 'unfit'
        }

        result = InputValidator.validate_medical_visit_data(data)

        assert result['visit_type'] == 'initial'
        assert result['visit_date'] == date(2020, 1, 15)
        assert result['result'] == 'unfit'

    def test_medical_visit_data_missing_visit_type_raises_error(self):
        """Should raise error for missing visit type."""
        data = {
            'visit_date': date(2020, 1, 15),
            'result': 'fit'
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_medical_visit_data(data)

    def test_medical_visit_data_missing_visit_date_raises_error(self):
        """Should raise error for missing visit date."""
        data = {
            'visit_type': 'periodic',
            'result': 'fit'
        }

        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_medical_visit_data(data)

        assert exc.value.field == "visit_date"

    def test_medical_visit_data_missing_result_raises_error(self):
        """Should raise error for missing result."""
        data = {
            'visit_type': 'periodic',
            'visit_date': date(2020, 1, 15)
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_medical_visit_data(data)

    def test_medical_visit_data_invalid_result_raises_error(self):
        """Should raise error for invalid result."""
        data = {
            'visit_type': 'periodic',
            'visit_date': date(2020, 1, 15),
            'result': 'invalid'
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_medical_visit_data(data)
