"""Input validation middleware for sanitizing query params and request bodies."""

import re

# Patterns for common injection attacks
SQL_INJECTION_PATTERN = re.compile(
    r"(--|;|/\*|\*/|\b(DROP|DELETE|INSERT|UPDATE|SELECT|UNION)\b\s)",
    re.IGNORECASE,
)
XSS_PATTERN = re.compile(r"(<script|javascript:|on\w+=)", re.IGNORECASE)
UUID_LIKE_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SEDIMENT_FILE_ID_PATTERN = re.compile(r"^file_[0-9a-f]+$")
ROOT_FILE_ID_PATTERN = re.compile(r"^file[-_][A-Za-z0-9]+$")


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize a string value.

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)[:max_length]

    # Truncate to max length
    value = value[:max_length]

    # Strip null bytes
    value = value.replace("\x00", "")

    return value


def validate_query_param(name: str, value: str, max_length: int = 200) -> str:
    """Validate and sanitize a query parameter.

    Args:
        name: Parameter name (for error messages)
        value: Parameter value
        max_length: Maximum allowed length

    Returns:
        Sanitized value

    Raises:
        ValueError: If value contains suspicious patterns
    """
    if not value:
        return value

    sanitized = sanitize_string(value, max_length)

    if SQL_INJECTION_PATTERN.search(sanitized):
        raise ValueError(f"Invalid characters in {name}")

    # Check for XSS patterns
    if XSS_PATTERN.search(sanitized):
        raise ValueError(f"Invalid characters in {name}")

    return sanitized


def validate_pagination(
    offset: int | None = None,
    limit: int | None = None,
    max_limit: int = 100,
) -> tuple[int, int]:
    """Validate pagination parameters.

    Args:
        offset: Requested offset (default: 0)
        limit: Requested limit (default: 50)
        max_limit: Maximum allowed limit

    Returns:
        Tuple of (offset, limit) with valid values
    """
    # Validate offset
    if offset is None:
        offset = 0
    offset = max(0, int(offset))

    # Validate limit
    if limit is None:
        limit = 50
    limit = max(1, min(int(limit), max_limit))

    return offset, limit


def validate_sort_order(order: str | None) -> str:
    """Validate sort order parameter.

    Args:
        order: Requested order ('asc' or 'desc')

    Returns:
        Valid order string ('asc' or 'desc')
    """
    if order is None:
        return "desc"

    order = str(order).lower().strip()
    if order not in ("asc", "desc"):
        return "desc"

    return order


def validate_sort_by(sort_by: str | None, allowed: list[str]) -> str:
    """Validate sort field parameter.

    Args:
        sort_by: Requested sort field
        allowed: List of allowed sort field names

    Returns:
        Valid sort field or first allowed value
    """
    if not allowed:
        return "date"

    if sort_by is None:
        return allowed[0]

    sort_by = str(sort_by).lower().strip()
    if sort_by not in allowed:
        return allowed[0]

    return sort_by


def validate_export_format(format: str | None, allowed: list[str]) -> str:
    """Validate export format parameter.

    Args:
        format: Requested format
        allowed: List of allowed formats

    Returns:
        Valid format string

    Raises:
        ValueError: If format is not allowed
    """
    if not format:
        raise ValueError("Export format is required")

    format = str(format).lower().strip()
    if format not in allowed:
        raise ValueError(f"Unsupported format: {format}. Allowed: {', '.join(allowed)}")

    return format


def validate_tag_name(tag: str) -> str:
    """Validate tag name.

    Args:
        tag: Tag name to validate

    Returns:
        Validated tag name

    Raises:
        ValueError: If tag is invalid
    """
    if not tag:
        raise ValueError("Tag name is required")

    tag = str(tag).strip()

    if len(tag) > 50:
        raise ValueError("Tag name must be 50 characters or less")

    # Only allow alphanumeric, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", tag):
        raise ValueError(
            "Tag name can only contain letters, numbers, hyphens, and underscores"
        )

    return tag.lower()


def validate_conversation_id(conversation_id: str) -> str:
    """Validate conversation ID format.

    Args:
        conversation_id: ID to validate

    Returns:
        Validated ID

    Raises:
        ValueError: If ID is invalid
    """
    if not conversation_id:
        raise ValueError("Conversation ID is required")

    conversation_id = str(conversation_id).strip()

    if len(conversation_id) > 100:
        raise ValueError("Conversation ID too long")

    # Allow alphanumeric characters plus hyphens and underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", conversation_id):
        raise ValueError("Invalid conversation ID format")

    return conversation_id


def validate_media_conversation_id(conversation_id: str) -> str:
    """Validate a conversation UUID used for media lookups."""
    if not conversation_id:
        raise ValueError("Conversation ID is required")

    conversation_id = str(conversation_id).strip().lower()
    if not UUID_LIKE_PATTERN.match(conversation_id):
        raise ValueError("Invalid conversation ID format")

    return conversation_id


def validate_media_file_id(file_id: str, *, root_level: bool = False) -> str:
    """Validate a media file identifier."""
    if not file_id:
        raise ValueError("File ID is required")

    file_id = str(file_id).strip()
    pattern = ROOT_FILE_ID_PATTERN if root_level else SEDIMENT_FILE_ID_PATTERN
    if not pattern.match(file_id):
        raise ValueError("Invalid file ID format")

    return file_id
