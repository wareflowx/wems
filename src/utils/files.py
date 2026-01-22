"""File operations utilities."""

import re
import shutil
from datetime import date
from pathlib import Path


def copy_document_to_storage(
    source_path: Path,
    category: str,
    employee_external_id: str,
    document_date: date,
    title: str,
    storage_root: Path = Path("documents"),
) -> Path:
    """
    Copy uploaded document to standardized storage location.

    Storage structure:
        documents/{category}/{external_id}_{YYYYMMDD}_{sanitized_title}.{ext}

    Args:
        source_path: Path to source document file
        category: Document category ('caces', 'medical', 'training')
        employee_external_id: Employee external ID for naming
        document_date: Date of the document
        title: Document title for filename
        storage_root: Root storage directory (default: "documents")

    Returns:
        Path to stored file

    Raises:
        FileNotFoundError: If source file doesn't exist
        ValueError: If category is invalid

    Example:
        >>> source = Path("/uploads/caces_cert.pdf")
        >>> stored = copy_document_to_storage(
        ...     source,
        ...     category="caces",
        ...     employee_external_id="WMS-001",
        ...     document_date=date(2026, 1, 15),
        ...     title="R489-1A Certification"
        ... )
        >>> print(stored)
        documents/caces/WMS-001_20260115_r489-1a_certification.pdf
    """
    # Validate source file exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    # Validate category
    valid_categories = ["caces", "medical", "training"]
    if category not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

    # Generate standardized filename
    filename = generate_document_name(
        category=category,
        employee_external_id=employee_external_id,
        document_date=document_date,
        title=title,
        extension=source_path.suffix,
    )

    # Create target path
    target_path = storage_root / category / filename

    # Ensure directory exists
    ensure_directory_exists(target_path.parent)

    # Copy file
    shutil.copy2(source_path, target_path)

    return target_path


def sanitize_filename(filename: str) -> str:
    """
    Remove/rename unsafe characters from filename.

    Removes:
    - Path traversal characters (..)
    - Special characters except letters, numbers, hyphens, underscores, dots
    - Leading/trailing spaces

    Replaces:
    - Spaces with underscores
    - Multiple consecutive underscores with single underscore

    Keeps:
    - Letters (a-z, A-Z)
    - Numbers (0-9)
    - Hyphens (-)
    - Underscores (_)
    - Dots (.)

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem

    Example:
        >>> sanitize_filename("My Document (2023)!.pdf")
        'my_document_2023_.pdf'
    """
    # Remove path traversal attempts
    filename = filename.replace("..", "")

    # Remove leading/trailing spaces
    filename = filename.strip()

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove unsafe characters (keep only alphanumeric, hyphen, underscore, dot)
    filename = re.sub(r"[^\w\-.]", "", filename)

    # Replace multiple consecutive underscores with single underscore
    filename = re.sub(r"_+", "_", filename)

    # Remove leading/trailing underscores that may have been created
    filename = filename.strip("_")

    # Ensure filename is not empty
    if not filename:
        filename = "document"

    return filename


def generate_document_name(
    category: str, employee_external_id: str, document_date: date, title: str, extension: str = ".pdf"
) -> str:
    """
    Generate standardized document name.

    Format: {external_id}_{category}_{YYYYMMDD}_{sanitized_title}{.ext}

    Args:
        category: Document category
        employee_external_id: Employee external ID
        document_date: Date of the document
        title: Document title
        extension: File extension (default: ".pdf")

    Returns:
        Standardized document filename

    Example:
        >>> name = generate_document_name(
        ...     category="caces",
        ...     employee_external_id="WMS-001",
        ...     document_date=date(2026, 1, 15),
        ...     title="R489-1A Certification",
        ...     extension=".pdf"
        ... )
        >>> print(name)
        'WMS-001_caces_20260115_r489-1a_certification.pdf'
    """
    # Sanitize title
    sanitized_title = sanitize_filename(title)

    # Format date as YYYYMMDD
    date_str = document_date.strftime("%Y%m%d")

    # Ensure extension has leading dot
    if extension and not extension.startswith("."):
        extension = "." + extension

    # Combine parts
    filename = f"{employee_external_id}_{category}_{date_str}_{sanitized_title}{extension}"

    return filename


def ensure_directory_exists(dir_path: Path) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        dir_path: Path to directory

    Example:
        >>> ensure_directory_exists(Path("documents/caces"))
        # Directory created if it didn't exist
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)


def validate_file_type(file_path: Path, allowed_extensions: list[str]) -> bool:
    """
    Validate file has allowed extension.

    Args:
        file_path: Path to file to validate
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.jpg'])

    Returns:
        True if file extension is allowed, False otherwise

    Example:
        >>> validate_file_type(Path("doc.pdf"), ['.pdf', '.doc'])
        True
        >>> validate_file_type(Path("doc.txt"), ['.pdf', '.doc'])
        False
    """
    # Normalize extensions (ensure they start with dot)
    normalized_allowed = []
    for ext in allowed_extensions:
        if not ext.startswith("."):
            ext = "." + ext
        normalized_allowed.append(ext.lower())

    # Get file extension and normalize
    file_ext = file_path.suffix.lower()

    return file_ext in normalized_allowed


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> size = get_file_size_mb(Path("document.pdf"))
        >>> print(f"File size: {size:.2f} MB")
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    return size_mb


def delete_document(file_path: Path) -> bool:
    """
    Delete document file.

    Args:
        file_path: Path to file to delete

    Returns:
        True if file was deleted, False if file didn't exist

    Example:
        >>> success = delete_document(Path("documents/caces/old_cert.pdf"))
        >>> if success:
        ...     print("Document deleted")
    """
    if not file_path.exists():
        return False

    file_path.unlink()
    return True


def move_document(source: Path, destination: Path) -> Path:
    """
    Move document from source to destination.

    Creates parent directories if needed.

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        Path to moved file

    Raises:
        FileNotFoundError: If source file doesn't exist

    Example:
        >>> moved = move_document(
        ...     Path("uploads/temp.pdf"),
        ...     Path("documents/caces/cert.pdf")
        ... )
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    # Ensure destination directory exists
    ensure_directory_exists(destination.parent)

    # Move file
    shutil.move(str(source), str(destination))

    return destination


def get_document_category_from_path(file_path: Path) -> str | None:
    """
    Extract document category from file path.

    Args:
        file_path: Path to document file

    Returns:
        Category string ('caces', 'medical', 'training') or None if not found

    Example:
        >>> get_document_category_from_path(Path("documents/caces/file.pdf"))
        'caces'
        >>> get_document_category_from_path(Path("documents/other/file.pdf"))
        None
    """
    valid_categories = ["caces", "medical", "training"]

    # Check if parent directory name is a valid category
    if file_path.parent.name in valid_categories:
        return file_path.parent.name

    return None


def is_valid_document_path(file_path: Path) -> bool:
    """
    Check if file path is a valid document path.

    Valid paths are under storage root with valid category.

    Args:
        file_path: Path to validate

    Returns:
        True if path is valid, False otherwise

    Example:
        >>> is_valid_document_path(Path("documents/caces/file.pdf"))
        True
        >>> is_valid_document_path(Path("other/file.pdf"))
        False
    """
    # Must be under documents directory
    if len(file_path.parts) < 2 or file_path.parts[0] != "documents":
        return False

    # Second part must be a valid category
    category = get_document_category_from_path(file_path)
    return category is not None
