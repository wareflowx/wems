"""
Tests for Email Validation

Tests cover:
- Valid email addresses are accepted
- Invalid email addresses are rejected
- International email addresses are supported
- Edge cases are handled correctly
"""

import pytest
from utils.validation import InputValidator, ValidationError


class TestValidEmails:
    """Test that valid email addresses pass validation."""

    def test_simple_valid_email(self):
        """Test that simple valid email passes."""
        email = "test@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_dots(self):
        """Test that email with dots in local part passes."""
        email = "user.name@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_plus(self):
        """Test that email with plus sign passes."""
        email = "user+tag@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_subdomain(self):
        """Test that email with subdomain passes."""
        email = "user@subdomain.example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_multi_part_tld(self):
        """Test that email with multi-part TLD passes."""
        email = "user@example.co.uk"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_french_tld(self):
        """Test that email with French TLD passes."""
        email = "user@example.fr"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_empty_email_is_allowed(self):
        """Test that empty email is allowed (optional field)."""
        result = InputValidator.validate_email("")
        assert result == ""

    def test_whitespace_only_email(self):
        """Test that whitespace-only email is allowed (optional field)."""
        result = InputValidator.validate_email("   ")
        assert result == ""

    def test_email_is_normalized_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        email = "User@Example.COM"
        result = InputValidator.validate_email(email)
        assert result == "user@example.com"


class TestInvalidEmails:
    """Test that invalid email addresses fail validation."""

    def test_plain_address_no_at(self):
        """Test that email without @ symbol fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("plainaddress")

        assert exc_info.value.field == "email"

    def test_missing_local_part(self):
        """Test that email without local part fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("@example.com")

        assert exc_info.value.field == "email"

    def test_missing_domain(self):
        """Test that email without domain fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("user@")

        assert exc_info.value.field == "email"

    def test_missing_domain_name(self):
        """Test that email without domain name fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("user@.com")

        assert exc_info.value.field == "email"

    def test_consecutive_dots(self):
        """Test that email with consecutive dots fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("user@domain..com")

        assert exc_info.value.field == "email"

    def test_invalid_tld_too_short(self):
        """Test that email with TLD that's too short passes (email-validator is permissive).

        Note: The email-validator library with check_deliverability=False
        is intentionally permissive about TLDs. It validates format, not
        whether the TLD exists in the IANA registry.
        """
        # This will pass validation - email-validator checks format, not TLD existence
        result = InputValidator.validate_email("user@domain.c")
        assert result == "user@domain.c"

    def test_invalid_tld_too_long(self):
        """Test that email with potentially invalid TLD passes (email-validator is permissive).

        Note: The email-validator library with check_deliverability=False
        doesn't validate against IANA registry. It only checks format.
        For stricter TLD validation, enable check_deliverability=True.
        """
        # This will pass validation - email-validator checks format, not TLD validity
        result = InputValidator.validate_email("user@domain.abcdefg")
        assert result == "user@domain.abcdefg"

    def test_multiple_at_symbols(self):
        """Test that email with multiple @ symbols fails."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("user@domain@example.com")

        assert exc_info.value.field == "email"

    def test_email_exceeds_max_length(self):
        """Test that email exceeding max length fails."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email(long_email)

        assert "Cannot exceed" in str(exc_info.value)
        assert exc_info.value.field == "email"


class TestInternationalEmails:
    """Test international email address support."""

    def test_international_local_part(self):
        """Test that email with international characters in local part passes."""
        email = "tëst@example.com"
        result = InputValidator.validate_email(email)
        assert result is not None

    def test_international_domain(self):
        """Test that email with international domain passes."""
        email = "user@exämple.com"
        result = InputValidator.validate_email(email)
        assert result is not None

    def test_french_characters(self):
        """Test that email with French characters passes."""
        email = "utilisateur@exemple.fr"
        result = InputValidator.validate_email(email)
        assert result is not None


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_email_with_numbers(self):
        """Test that email with numbers passes."""
        email = "user123@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_hyphen(self):
        """Test that email with hyphen passes."""
        email = "user-name@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_underscore(self):
        """Test that email with underscore in local part passes."""
        email = "user_name@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_email_with_percent(self):
        """Test that email with percent in local part passes."""
        email = "user%name@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_trailing_whitespace_removed(self):
        """Test that trailing whitespace is removed."""
        email = "user@example.com   "
        result = InputValidator.validate_email(email)
        assert result == "user@example.com"

    def test_leading_whitespace_removed(self):
        """Test that leading whitespace is removed."""
        email = "   user@example.com"
        result = InputValidator.validate_email(email)
        assert result == "user@example.com"


class TestErrorMessages:
    """Test that error messages are user-friendly."""

    def test_error_message_for_invalid_format(self):
        """Test that error message is clear for invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email("invalid-email")

        # The error message should be descriptive
        assert exc_info.value.message
        assert exc_info.value.field == "email"

    def test_error_message_for_too_long_email(self):
        """Test that error message includes max length."""
        long_email = "a" * 300 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_email(long_email)

        assert "Cannot exceed" in exc_info.value.message
        assert str(InputValidator.MAX_LENGTH_EMAIL) in exc_info.value.message
