"""Tests for file validation utilities.

These tests ensure security against path traversal attacks and
proper validation of file uploads.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.file_validation import (
    validate_document_path,
    sanitize_file_path,
    is_safe_filename,
    validate_and_copy_document,
    FileValidationError,
)


class TestValidateDocumentPath:
    """Test suite for validate_document_path function."""

    def test_valid_file_in_documents_dir(self, db):
        """Test validation of valid file in documents directory."""
        # Create test directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            test_file = docs_dir / "test.pdf"
            test_file.write_text("test content")

            # Validate
            is_valid, error = validate_document_path(
                str(test_file),
                allowed_dir=docs_dir
            )

            assert is_valid is True
            assert error is None

    def test_path_traversal_with_double_dot(self, db):
        """Test that path traversal with ../ is blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # Try to access parent directory
            malicious_path = docs_dir.parent / "secret.txt"

            is_valid, error = validate_document_path(
                str(malicious_path),
                allowed_dir=docs_dir
            )

            assert is_valid is False
            assert "path traversal" in error.lower() or "within" in error.lower()

    def test_path_traversal_with_encoded_dots(self, db):
        """Test that encoded path traversal is blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # Try various path traversal patterns
            traversal_patterns = [
                "../etc/passwd",
                "..\\..\\windows\\system32",
                "./../../etc/passwd",
                "....//....//etc/passwd",
            ]

            for pattern in traversal_patterns:
                is_valid, error = validate_document_path(
                    pattern,
                    allowed_dir=docs_dir
                )

                assert is_valid is False, f"Should block: {pattern}"

    def test_absolute_path_blocked(self, db):
        """Test that absolute paths outside allowed dir are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # Create file outside allowed directory
            external_file = Path(tmpdir) / "external.pdf"
            external_file.write_text("content")

            is_valid, error = validate_document_path(
                str(external_file),
                allowed_dir=docs_dir
            )

            assert is_valid is False
            assert "within" in error.lower()

    def test_nonexistent_file(self, db):
        """Test that nonexistent files are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            nonexistent = docs_dir / "does_not_exist.pdf"

            is_valid, error = validate_document_path(
                str(nonexistent),
                allowed_dir=docs_dir
            )

            assert is_valid is False
            assert "does not exist" in error.lower()

    def test_directory_rejected(self, db):
        """Test that directories are rejected (must be a file)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            is_valid, error = validate_document_path(
                str(docs_dir),
                allowed_dir=docs_dir
            )

            assert is_valid is False
            assert "must be a file" in error.lower()

    def test_allowed_extension_validation(self, db):
        """Test that file extension is validated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # Test with .exe file (not allowed)
            exe_file = docs_dir / "malicious.exe"
            exe_file.write_text("content")

            is_valid, error = validate_document_path(
                str(exe_file),
                allowed_dir=docs_dir,
                allowed_extensions={".pdf", ".png"}
            )

            assert is_valid is False
            assert "only" in error.lower() or "allowed" in error.lower()

    def test_file_size_validation(self, db):
        """Test that file size is validated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # Create large file (> 1MB for this test)
            large_file = docs_dir / "large.pdf"
            large_file.write_bytes(b"x" * (2 * 1024 * 1024))  # 2MB

            is_valid, error = validate_document_path(
                str(large_file),
                allowed_dir=docs_dir,
                max_size_mb=1
            )

            assert is_valid is False
            assert "exceeds maximum" in error.lower() or "size" in error.lower()

    def test_valid_pdf_file(self, db):
        """Test that valid PDF files pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            pdf_file = docs_dir / "certificate.pdf"
            pdf_file.write_bytes(b"%PDF-1.4")

            is_valid, error = validate_document_path(
                str(pdf_file),
                allowed_dir=docs_dir,
                allowed_extensions={".pdf"},
                max_size_mb=10
            )

            assert is_valid is True
            assert error is None

    def test_valid_image_files(self, db):
        """Test that valid image files pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            for ext in [".png", ".jpg", ".jpeg"]:
                img_file = docs_dir / f"image{ext}"
                img_file.write_bytes(b"fake_image_data")

                is_valid, error = validate_document_path(
                    str(img_file),
                    allowed_dir=docs_dir,
                    allowed_extensions={".pdf", ".png", ".jpg", ".jpeg"}
                )

                assert is_valid is True, f"Failed for {ext}"
                assert error is None

    def test_empty_path_rejected(self, db):
        """Test that empty paths are rejected."""
        is_valid, error = validate_document_path("")

        assert is_valid is False
        assert "required" in error.lower()

    def test_none_path_rejected(self, db):
        """Test that None paths are rejected."""
        is_valid, error = validate_document_path(None)

        assert is_valid is False
        assert "required" in error.lower()

    def test_unc_path_blocked(self, db):
        """Test that Windows UNC paths are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "documents"
            docs_dir.mkdir()

            # UNC path: \\evil-server\share\malware.exe
            unc_path = r"\\evil-server\share\file.pdf"

            is_valid, error = validate_document_path(
                unc_path,
                allowed_dir=docs_dir
            )

            # Should be rejected as invalid path or not within allowed dir
            assert is_valid is False


class TestSanitizeFilePath:
    """Test suite for sanitize_file_path function."""

    def test_removes_double_dots(self):
        """Test that .. is removed."""
        assert sanitize_file_path("../../etc/passwd") == "etcpasswd"
        assert sanitize_file_path("../../../test") == "test"

    def test_removes_slashes(self):
        """Test that / and \\ are removed."""
        assert sanitize_file_path("path/to/file") == "pathtofile"
        assert sanitize_file_path("path\\to\\file") == "pathtofile"

    def test_removes_null_bytes(self):
        """Test that null bytes are removed."""
        assert sanitize_file_path("file\x00.pdf") == "file.pdf"

    def test_removes_control_characters(self):
        """Test that control characters are removed."""
        assert sanitize_file_path("file\r\n.pdf") == "file.pdf"

    def test_keeps_safe_filenames(self):
        """Test that safe filenames are unchanged."""
        assert sanitize_file_path("document.pdf") == "document.pdf"
        assert sanitize_file_path("certificate-2024.pdf") == "certificate-2024.pdf"
        assert sanitize_file_path("image_v1.png") == "image_v1.png"


class TestIsSafeFilename:
    """Test suite for is_safe_filename function."""

    def test_safe_filenames(self):
        """Test that safe filenames return True."""
        safe_names = [
            "document.pdf",
            "certificate-2024.pdf",
            "image_v1.png",
            "CACES_R489.pdf",
            "visite_medicale.pdf",
        ]

        for name in safe_names:
            assert is_safe_filename(name), f"Should be safe: {name}"

    def test_path_traversal_detected(self):
        """Test that path traversal is detected."""
        unsafe = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "./../../test",
            "../file.pdf",
        ]

        for name in unsafe:
            assert is_safe_filename(name) is False, f"Should be unsafe: {name}"

    def test_slashes_detected(self):
        """Test that slashes are detected."""
        assert is_safe_filename("path/to/file") is False
        assert is_safe_filename("path\\to\\file") is False

    def test_null_bytes_detected(self):
        """Test that null bytes are detected."""
        assert is_safe_filename("file\x00.pdf") is False

    def test_empty_filename(self):
        """Test that empty filename is unsafe."""
        assert is_safe_filename("") is False
        assert is_safe_filename(None) is False

    def test_windows_reserved_names(self):
        """Test that Windows reserved names are blocked."""
        reserved = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4",
            "LPT1", "LPT2", "LPT3",
        ]

        for name in reserved:
            assert is_safe_filename(name) is False, f"Should block reserved: {name}"

    def test_windows_reserved_with_extension(self):
        """Test that Windows reserved names with extensions are blocked."""
        assert is_safe_filename("CON.pdf") is False
        assert is_safe_filename("NUL.txt") is False


class TestValidateAndCopyDocument:
    """Test suite for validate_and_copy_document function."""

    def test_valid_file_copied_to_secure_storage(self, db):
        """Test that valid files are copied to secure storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            source_dir = Path(tmpdir) / "uploads"
            source_dir.mkdir()
            source_file = source_dir / "cert.pdf"
            source_file.write_text("certificate content")

            # Set destination
            dest_dir = Path(tmpdir) / "documents"

            # Copy to secure storage
            success, error, secure_path = validate_and_copy_document(
                str(source_file),
                dest_dir=dest_dir
            )

            assert success is True
            assert error is None
            assert secure_path is not None

            # Verify file was copied
            secure = Path(secure_path)
            assert secure.exists()
            assert secure.parent == dest_dir.resolve()

            # Verify content
            assert secure.read_text() == "certificate content"

    def test_invalid_extension_rejected(self, db):
        """Test that files with invalid extensions are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "malicious.exe"
            source_file.write_text("malware")

            success, error, secure_path = validate_and_copy_document(
                str(source_file),
                allowed_extensions={".pdf", ".png"}
            )

            assert success is False
            assert error is not None
            assert secure_path is None

    def test_oversized_file_rejected(self, db):
        """Test that oversized files are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            large_file = Path(tmpdir) / "large.pdf"
            large_file.write_bytes(b"x" * (2 * 1024 * 1024))  # 2MB

            success, error, secure_path = validate_and_copy_document(
                str(large_file),
                max_size_mb=1
            )

            assert success is False
            assert "size" in error.lower()

    def test_unique_filename_generated(self, db):
        """Test that unique filenames are generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "uploads"
            source_dir.mkdir()
            source_file = source_dir / "cert.pdf"
            source_file.write_text("content")

            dest_dir = Path(tmpdir) / "documents"

            # Copy twice with same source
            _, _, path1 = validate_and_copy_document(str(source_file), dest_dir=dest_dir)
            _, _, path2 = validate_and_copy_document(str(source_file), dest_dir=dest_dir)

            # Paths should be different (unique UUIDs)
            assert path1 != path2

    def test_creates_destination_directory(self, db):
        """Test that destination directory is created if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "cert.pdf"
            source_file.write_text("content")

            dest_dir = Path(tmpdir) / "documents" / "nested" / "dir"

            # Directory doesn't exist yet
            assert not dest_dir.exists()

            success, error, secure_path = validate_and_copy_document(
                str(source_file),
                dest_dir=dest_dir
            )

            assert success is True
            assert dest_dir.exists()
            assert Path(secure_path).parent == dest_dir.resolve()
