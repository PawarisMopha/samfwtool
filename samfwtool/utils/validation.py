"""
Input validation utilities for SamFWTool

Provides secure input validation to prevent path traversal,
injection attacks, and other security issues.

Author: SamFWTool Team
License: MIT
"""
import os
import re
from pathlib import Path
from typing import Optional, List

from samfwtool.exceptions import PathValidationError, ValidationError

__all__ = [
    "validate_path",
    "validate_firmware_path",
    "validate_output_path",
    "validate_partition_name",
    "sanitize_filename",
    "is_safe_path",
]


def validate_path(
    path: str,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allowed_extensions: Optional[List[str]] = None,
    base_dir: Optional[Path] = None,
) -> Path:
    """
    Validate a file system path for security and correctness.

    Args:
        path: The path to validate
        must_exist: If True, path must exist
        must_be_file: If True, path must be a file
        must_be_dir: If True, path must be a directory
        allowed_extensions: List of allowed file extensions (e.g., ['.tar', '.zip'])
        base_dir: If provided, path must be within this directory

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid or unsafe
    """
    if not path:
        raise PathValidationError("Path cannot be empty", path)

    # Convert to Path object
    try:
        p = Path(path).resolve()
    except (ValueError, OSError) as e:
        raise PathValidationError(f"Invalid path: {e}", path)

    # Check for path traversal attempts
    if ".." in str(path):
        # Allow .. only if it resolves within base_dir
        if base_dir:
            try:
                p.relative_to(base_dir.resolve())
            except ValueError:
                raise PathValidationError("Path traversal detected", path)

    # Check existence
    if must_exist and not p.exists():
        raise PathValidationError("Path does not exist", str(p))

    # Check file/directory
    if must_be_file and p.exists() and not p.is_file():
        raise PathValidationError("Path is not a file", str(p))

    if must_be_dir and p.exists() and not p.is_dir():
        raise PathValidationError("Path is not a directory", str(p))

    # Check extension
    if allowed_extensions:
        # Handle multi-part extensions like .tar.md5
        full_suffix = "".join(p.suffixes).lower()
        if not any(full_suffix.endswith(ext.lower()) for ext in allowed_extensions):
            raise PathValidationError(
                f"Invalid file extension. Allowed: {allowed_extensions}", str(p)
            )

    # Check base directory constraint
    if base_dir:
        try:
            p.relative_to(base_dir.resolve())
        except ValueError:
            raise PathValidationError(
                f"Path must be within {base_dir}", str(p)
            )

    return p


def validate_firmware_path(path: str) -> Path:
    """
    Validate a firmware file path.

    Args:
        path: Path to firmware file

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid
    """
    allowed_extensions = [
        ".tar",
        ".tar.md5",
        ".zip",
        ".img",
        ".bin",
        ".lz4",
        ".gz",
        ".xz",
    ]

    return validate_path(
        path,
        must_exist=True,
        must_be_file=True,
        allowed_extensions=allowed_extensions,
    )


def validate_output_path(path: str, create_parents: bool = False) -> Path:
    """
    Validate an output path.

    Args:
        path: Output path
        create_parents: If True, create parent directories if needed

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid
    """
    p = validate_path(path)

    # Create parent directories if requested
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)

    return p


def validate_partition_name(name: str) -> str:
    """
    Validate a partition name.

    Args:
        name: Partition name to validate

    Returns:
        Validated partition name

    Raises:
        ValidationError: If partition name is invalid
    """
    if not name:
        raise ValidationError("Partition name cannot be empty")

    # Allow alphanumeric, underscore, hyphen, and dot
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', name):
        raise ValidationError(
            f"Invalid partition name: {name}. "
            "Only alphanumeric characters, underscore, hyphen, and dot allowed."
        )

    # Check length
    if len(name) > 255:
        raise ValidationError("Partition name too long (max 255 characters)")

    return name


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing unsafe characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"

    # Remove path separators
    filename = os.path.basename(filename)

    # Remove null bytes and other control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)

    # Replace potentially dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure non-empty
    if not filename:
        return "unnamed"

    return filename


def is_safe_path(path: str, base_dir: Optional[Path] = None) -> bool:
    """
    Check if a path is safe (no traversal attacks).

    Args:
        path: Path to check
        base_dir: If provided, path must be within this directory

    Returns:
        True if path is safe, False otherwise
    """
    try:
        validate_path(path, base_dir=base_dir)
        return True
    except (PathValidationError, ValidationError):
        return False
