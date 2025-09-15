"""Custom exceptions for external service integrations."""


class ZapSignAPIError(Exception):
    """Base exception for ZapSign API errors."""

    pass


class ZapSignAuthenticationError(ZapSignAPIError):
    """Raised when authentication with ZapSign API fails."""

    pass


class ZapSignValidationError(ZapSignAPIError):
    """Raised when ZapSign API returns validation errors."""

    pass