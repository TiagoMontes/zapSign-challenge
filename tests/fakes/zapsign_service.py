"""Fake ZapSign service for testing."""

from typing import Optional, Dict, Any
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class FakeZapSignService:
    """Fake implementation of ZapSign service for testing."""

    def __init__(self):
        """Initialize fake service."""
        self.should_fail_auth = False
        self.should_fail_validation = False
        self.should_fail_api = False
        self.last_delete_call: Optional[Dict[str, Any]] = None

    def delete_document(self, api_token: str, doc_token: str) -> bool:
        """Fake delete document implementation."""
        # Record the call for test verification
        self.last_delete_call = {
            "api_token": api_token,
            "doc_token": doc_token
        }

        # Simulate various failure scenarios
        if self.should_fail_auth:
            raise ZapSignAuthenticationError("Invalid API token")

        if self.should_fail_validation:
            raise ZapSignValidationError("Invalid document token")

        if self.should_fail_api:
            raise ZapSignAPIError("ZapSign API is unavailable")

        # Simulate success
        return True

    def set_auth_failure(self, should_fail: bool = True) -> None:
        """Configure the fake to simulate authentication failure."""
        self.should_fail_auth = should_fail

    def set_validation_failure(self, should_fail: bool = True) -> None:
        """Configure the fake to simulate validation failure."""
        self.should_fail_validation = should_fail

    def set_api_failure(self, should_fail: bool = True) -> None:
        """Configure the fake to simulate API failure."""
        self.should_fail_api = should_fail

    def reset(self) -> None:
        """Reset the fake to initial state."""
        self.should_fail_auth = False
        self.should_fail_validation = False
        self.should_fail_api = False
        self.last_delete_call = None