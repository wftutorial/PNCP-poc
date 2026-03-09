"""Unified error response schema for SmartLic API.

SYS-011 / DEBT-015: Centralizes error codes and structured error response
builder so all routes can produce consistent, machine-readable error bodies.

Backward compatibility:
- SearchErrorCode is kept as an alias so existing imports in schemas.py and
  routes/search.py continue to work without changes.
"""

from datetime import datetime, timezone
from enum import Enum


class ErrorCode(str, Enum):
    """Semantic error codes — orthogonal to HTTP status codes.

    Used in structured error responses across all API endpoints.
    Original search-specific codes (CRIT-009 AC2) preserved verbatim so that
    frontend error-message mappings remain intact.
    """

    # --- Search / pipeline errors (original CRIT-009 set) ---
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    ALL_SOURCES_FAILED = "ALL_SOURCES_FAILED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # --- General / cross-cutting errors (SYS-011 additions) ---
    AUTH_ERROR = "AUTH_ERROR"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BILLING_ERROR = "BILLING_ERROR"


# Backward-compatibility alias — existing code that imports SearchErrorCode from
# schemas.py will continue to work; schemas.py re-exports this alias.
SearchErrorCode = ErrorCode


def build_error_detail(
    message: str,
    error_code: ErrorCode,
    **kwargs,
) -> dict:
    """Build a structured error response body suitable for HTTPException.detail.

    Args:
        message: Human-readable error message.
        error_code: Machine-readable ErrorCode enum value.
        **kwargs: Optional extra fields merged into the response dict (e.g.
            search_id, correlation_id, user_id).  None values are included so
            callers can be explicit; strip them client-side if desired.

    Returns:
        dict with at minimum: detail, error_code, timestamp — plus any kwargs.

    Never exposes stack traces or internal information.
    """
    payload: dict = {
        "detail": message,
        "error_code": error_code.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    payload.update(kwargs)
    return payload
