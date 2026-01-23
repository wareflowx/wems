"""File validation utilities to prevent path traversal attacks.

This module provides secure file path validation and sanitization functions
to prevent path traversal vulnerabilities and ensure files are within
allowed directories.

Security Features:
- Path traversal prevention (../, ..\\)
- Absolute path blocking
- UNC path blocking (Windows)
- File type validation (extension and magic numbers)
- File size validation
- File existence checking
- PDF structure validation
- Filename sanitization
- Empty file detection
"""

import os
from pathlib import Path
from typing import Tuple, Optional, Set

# Try to import optional dependencies for enhanced validation
# These are not required for basic functionality but provide better security
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    pypdf = None
    PYPDF_AVAILABLE = False


class FileValidationError(Exception):
    """Raised when file validation fails."""

    pass


# Configuration
DEFAULT_ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
DEFAULT_MAX_FILE_SIZE_MB = 10
DEFAULT_DOCUMENTS_DIR = Path("documents")

# MIME types for magic number validation
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
}

# File extension to MIME type mapping
EXTENSION_TO_MIME = {
    '.pdf': 'application/pdf',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
}


def validate_document_path(
    file_path: str,
    allowed_dir: Optional[Path] = None,
    allowed_extensions: Optional[set] = None,
    max_size_mb: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate document path is within allowed directory and meets security requirements.

    This function prevents path traversal attacks by:
    - Resolving the absolute path
    - Checking it's within the allowed directory
    - Validating file extension
    - Checking file size

    Args:
        file_path: Path to validate
        allowed_dir: Directory where files are allowed (default: documents/)
        allowed_extensions: Set of allowed file extensions (default: .pdf, .png, .jpg, .jpeg)
        max_size_mb: Maximum file size in MB (default: 10)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> is_valid, error = validate_document_path("documents/cert.pdf")
        >>> if is_valid:
        ...     print("File is valid")
        ... else:
        ...     print(f"Error: {error}")

    Security:
        - Blocks path traversal: ../../etc/passwd
        - Blocks absolute paths: C:\\Windows\\System32
        - Blocks UNC paths: \\\\evil-server\\share
        - Validates file extension
        - Validates file size
    """
    if not file_path:
        return False, "File path is required"

    # Use default allowed directory if not specified
    if allowed_dir is None:
        allowed_dir = DEFAULT_DOCUMENTS_DIR

    if allowed_extensions is None:
        allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS

    if max_size_mb is None:
        max_size_mb = DEFAULT_MAX_FILE_SIZE_MB

    try:
        path = Path(file_path).resolve()
        allowed_resolved = allowed_dir.resolve()

        # Security check 1: Ensure path is within allowed directory
        # This prevents path traversal attacks
        try:
            path.relative_to(allowed_resolved)
        except ValueError:
            return False, (
                f"File must be within '{allowed_dir}' directory. "
                f"Path traversal is not allowed."
            )

        # Security check 2: File must exist
        if not path.exists():
            return False, "File does not exist"

        # Security check 3: Must be a file, not a directory
        if not path.is_file():
            return False, "Path must be a file, not a directory"

        # Security check 4: Validate file extension
        if path.suffix.lower() not in allowed_extensions:
            allowed_str = ", ".join(sorted(allowed_extensions))
            return False, f"Only {allowed_str} files are allowed"

        # Security check 5: Validate file size
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"

        # All checks passed
        return True, None

    except PermissionError:
        return False, "Permission denied accessing file"
    except OSError as e:
        return False, f"Invalid file path: {e}"
    except Exception as e:
        return False, f"Error validating file: {e}"


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize file path by removing dangerous characters.

    This function removes or escapes characters that could be used
    in path traversal attacks.

    Args:
        file_path: Path to sanitize

    Returns:
        Sanitized path string

    Examples:
        >>> sanitize_file_path("../../../etc/passwd")
        'etcpasswd'
        >>> sanitize_file_path("normal_file.pdf")
        'normal_file.pdf'
    """
    # Remove path traversal sequences
    sanitized = file_path.replace("..", "").replace("\\", "").replace("/", "")

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

    # Remove control characters
    sanitized = "".join(char for char in sanitized if ord(char) >= 32)

    return sanitized


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe (no path traversal or special characters).

    Args:
        filename: Filename to check

    Returns:
        True if filename is safe, False otherwise

    Examples:
        >>> is_safe_filename("document.pdf")
        True
        >>> is_safe_filename("../../etc/passwd")
        False
        >>> is_safe_filename("file\x00.pdf")
        False
    """
    if not filename:
        return False

    # Check for path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False

    # Check for null bytes
    if "\x00" in filename:
        return False

    # Check for control characters
    if any(ord(char) < 32 for char in filename):
        return False

    # Check for Windows reserved names
    base_name = filename.split(".")[0].upper()
    windows_reserved = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }
    if base_name in windows_reserved:
        return False

    return True


def validate_file_basic(
    file_path: str,
    allowed_extensions: Optional[set] = None,
    max_size_mb: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate file basic properties (extension, size, existence).

    This does NOT check if file is in a specific directory.
    Use this for validating user-selected files before copying.

    Args:
        file_path: Path to validate
        allowed_extensions: Allowed file extensions
        max_size_mb: Maximum file size in MB

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path is required"

    if allowed_extensions is None:
        allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS

    if max_size_mb is None:
        max_size_mb = DEFAULT_MAX_FILE_SIZE_MB

    try:
        path = Path(file_path).resolve()

        # Check file exists
        if not path.exists():
            return False, "File does not exist"

        # Must be a file, not a directory
        if not path.is_file():
            return False, "Path must be a file, not a directory"

        # Validate file extension
        if path.suffix.lower() not in allowed_extensions:
            allowed_str = ", ".join(sorted(allowed_extensions))
            return False, f"Only {allowed_str} files are allowed"

        # Validate file size
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"

        return True, None

    except PermissionError:
        return False, "Permission denied accessing file"
    except OSError as e:
        return False, f"Invalid file path: {e}"
    except Exception as e:
        return False, f"Error validating file: {e}"


def validate_magic_number(
    file_path: Path,
    expected_mime: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate file type using magic number detection.

    This function checks the actual file content (magic numbers) rather than
    just the file extension, preventing file type spoofing attacks.

    Args:
        file_path: Path to the file to validate
        expected_mime: Expected MIME type (if None, checks against all allowed)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> is_valid, error = validate_magic_number(Path("file.pdf"))
        >>> if is_valid:
        ...     print("File content matches extension")
        ... else:
        ...     print(f"Error: {error}")
    """
    if not MAGIC_AVAILABLE:
        # If python-magic is not available, log warning but don't fail
        # (graceful degradation for environments where libmagic is not available)
        import sys
        print(
            "[WARNING] python-magic not available, skipping magic number validation. "
            "Install python-magic and libmagic for enhanced security.",
            file=sys.stderr
        )
        return True, None

    try:
        # Detect MIME type from file content
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_file(str(file_path))

        # Check if detected type is allowed
        if detected_mime not in ALLOWED_MIME_TYPES:
            allowed_str = ", ".join(sorted(ALLOWED_MIME_TYPES))
            return False, (
                f"Invalid file content type: {detected_mime}. "
                f"Allowed: {allowed_str}"
            )

        # If expected MIME is provided, verify it matches
        if expected_mime is not None and detected_mime != expected_mime:
            return False, (
                f"File content ({detected_mime}) does not match "
                f"expected type ({expected_mime}). "
                f"File may have been renamed."
            )

        return True, None

    except Exception as e:
        return False, f"Failed to validate file type: {e}"


def validate_pdf_structure(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate PDF file structure.

    This function checks if a PDF file is valid and can be read.
    It verifies the PDF has pages and is not corrupted.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> is_valid, error = validate_pdf_structure(Path("document.pdf"))
        >>> if is_valid:
        ...     print("PDF structure is valid")
    """
    if not PYPDF_AVAILABLE:
        # If pypdf is not available, log warning but don't fail
        import sys
        print(
            "[WARNING] pypdf not available, skipping PDF structure validation. "
            "Install pypdf for enhanced PDF validation.",
            file=sys.stderr
        )
        return True, None

    try:
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)

            # Check if PDF has pages
            if len(reader.pages) == 0:
                return False, "PDF file has no pages"

            # Check if PDF is encrypted (we reject encrypted PDFs for security)
            if reader.is_encrypted:
                return False, "Encrypted PDF files are not allowed"

        return True, None

    except Exception as e:
        return False, f"Invalid PDF file: {e}"


def validate_filename_characters(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate filename for suspicious or dangerous characters.

    This function checks for:
    - Suspicious characters that could break file systems
    - Excessively long filenames
    - Null bytes

    Args:
        filename: The filename to validate (without path)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> is_valid, error = validate_filename_characters("document.pdf")
        >>> if is_valid:
        ...     print("Filename is safe")
    """
    if not filename:
        return False, "Filename is empty"

    # Check for null bytes
    if '\x00' in filename:
        return False, "Filename contains null bytes"

    # Check for suspicious characters (Windows/Unix problematic characters)
    suspicious_chars = ['<', '>', ':', '|', '"', '*', '?', '\x00']
    if any(char in filename for char in suspicious_chars):
        return False, f"Filename contains invalid characters: {', '.join(suspicious_chars)}"

    # Check for excessively long names (filesystem limit)
    # Windows has a 255 character limit for filenames
    if len(filename) > 255:
        return False, f"Filename too long ({len(filename)} chars, max 255)"

    return True, None


def validate_file_not_empty(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate that file is not empty (size > 0 bytes).

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        size = file_path.stat().st_size
        if size == 0:
            return False, "File is empty (0 bytes)"
        return True, None
    except Exception as e:
        return False, f"Failed to check file size: {e}"


def validate_comprehensive(
    file_path: str,
    allowed_extensions: Optional[Set[str]] = None,
    max_size_mb: Optional[int] = None,
    validate_magic: bool = True,
    validate_pdf: bool = True,
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive file validation with all security checks.

    This function performs the following validations:
    1. File existence and basic checks
    2. File extension validation
    3. File size validation (upper and lower bounds)
    4. Magic number validation (if enabled)
    5. PDF structure validation (if enabled and file is PDF)
    6. Filename character validation
    7. Empty file detection

    Args:
        file_path: Path to the file to validate
        allowed_extensions: Allowed file extensions (default: DEFAULT_ALLOWED_EXTENSIONS)
        max_size_mb: Maximum file size in MB (default: DEFAULT_MAX_FILE_SIZE_MB)
        validate_magic: Whether to validate magic numbers (default: True)
        validate_pdf: Whether to validate PDF structure (default: True)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> is_valid, error = validate_comprehensive("document.pdf")
        >>> if is_valid:
        ...     print("File passed all security checks")
        ... else:
        ...     print(f"Security check failed: {error}")
    """
    if allowed_extensions is None:
        allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS
    if max_size_mb is None:
        max_size_mb = DEFAULT_MAX_FILE_SIZE_MB

    try:
        path = Path(file_path).resolve()

        # Check 1: File exists
        if not path.exists():
            return False, "File does not exist"

        # Check 2: Is a file (not directory)
        if not path.is_file():
            return False, "Path must be a file, not a directory"

        # Check 3: Validate filename characters
        filename_ok, filename_error = validate_filename_characters(path.name)
        if not filename_ok:
            return False, filename_error

        # Check 4: File extension
        if path.suffix.lower() not in allowed_extensions:
            allowed_str = ", ".join(sorted(allowed_extensions))
            return False, f"Invalid file type. Allowed: {allowed_str}"

        # Check 5: File size (upper bound)
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File too large ({size_mb:.1f}MB). Maximum: {max_size_mb}MB"

        # Check 6: File is not empty
        not_empty_ok, not_empty_error = validate_file_not_empty(path)
        if not not_empty_ok:
            return False, not_empty_error

        # Check 7: Magic number validation
        if validate_magic:
            expected_mime = EXTENSION_TO_MIME.get(path.suffix.lower())
            magic_ok, magic_error = validate_magic_number(path, expected_mime)
            if not magic_ok:
                return False, magic_error

        # Check 8: PDF structure validation (for PDF files)
        if validate_pdf and path.suffix.lower() == '.pdf':
            pdf_ok, pdf_error = validate_pdf_structure(path)
            if not pdf_ok:
                return False, pdf_error

        return True, None

    except PermissionError:
        return False, "Permission denied accessing file"
    except OSError as e:
        return False, f"Invalid file path: {e}"
    except Exception as e:
        return False, f"Error validating file: {e}"


def validate_and_copy_document(
    source_path: str,
    dest_dir: Optional[Path] = None,
    allowed_extensions: Optional[set] = None,
    max_size_mb: Optional[int] = None,
    validate_magic: bool = True,
    validate_pdf: bool = True,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate document and copy to secure storage directory.

    This is the recommended function for handling document uploads:
    1. Validates the source path with comprehensive security checks
    2. Generates a unique filename
    3. Copies file to secure storage
    4. Returns the new secure path

    Security validations performed:
    - File existence and basic checks
    - File extension validation
    - File size validation (upper and lower bounds)
    - Magic number validation (if enabled)
    - PDF structure validation (if enabled and file is PDF)
    - Filename character validation
    - Empty file detection

    Args:
        source_path: Original file path selected by user
        dest_dir: Destination directory (default: documents/)
        allowed_extensions: Allowed file extensions
        max_size_mb: Maximum file size in MB
        validate_magic: Whether to validate magic numbers (default: True)
        validate_pdf: Whether to validate PDF structure (default: True)

    Returns:
        Tuple of (success, error_message, secure_path)

    Examples:
        >>> success, error, path = validate_and_copy_document(
        ...     "/user/uploads/cert.pdf"
        ... )
        >>> if success:
        ...     print(f"File saved to: {path}")
        ... else:
        ...     print(f"Error: {error}")
    """
    import uuid
    import shutil

    if dest_dir is None:
        dest_dir = DEFAULT_DOCUMENTS_DIR

    # Validate source file with comprehensive checks
    is_valid, error_msg = validate_comprehensive(
        source_path,
        allowed_extensions=allowed_extensions,
        max_size_mb=max_size_mb,
        validate_magic=validate_magic,
        validate_pdf=validate_pdf
    )

    if not is_valid:
        return False, error_msg, None

    try:
        source = Path(source_path).resolve()
        dest_resolved = dest_dir.resolve()
        dest_resolved.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to prevent overwrites
        unique_name = f"{uuid.uuid4()}_{source.name}"
        dest_path = dest_resolved / unique_name

        # Copy file to secure storage
        shutil.copy2(source, dest_path)

        return True, None, str(dest_path)

    except Exception as e:
        return False, f"Failed to copy file: {e}", None
