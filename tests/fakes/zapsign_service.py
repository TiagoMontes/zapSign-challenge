"""Fake ZapSign service for testing."""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)
from core.domain.value_objects.zapsign_response import ZapSignSignerResponse


class FakeZapSignService:
    """Fake implementation of ZapSign service for testing."""

    def __init__(self):
        """Initialize fake service."""
        self.should_fail_auth = False
        self.should_fail_validation = False
        self.should_fail_api = False
        self.last_delete_call: Optional[Dict[str, Any]] = None
        self.last_get_signer_call: Optional[Dict[str, Any]] = None
        self.mock_signer_data: Optional[Dict[str, Any]] = None

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

    def get_signer_by_token(self, api_token: str, signer_token: str) -> ZapSignSignerResponse:
        """Fake get signer by token implementation."""
        # Record the call for test verification
        self.last_get_signer_call = {
            "api_token": api_token,
            "signer_token": signer_token
        }

        # Simulate various failure scenarios
        if self.should_fail_auth:
            raise ZapSignAuthenticationError("Invalid API token")

        if self.should_fail_validation:
            raise ZapSignValidationError("Invalid signer token")

        if self.should_fail_api:
            raise ZapSignAPIError("ZapSign API is unavailable")

        # Return mock data if provided, otherwise default data
        if self.mock_signer_data:
            return ZapSignSignerResponse.from_api_data(self.mock_signer_data)

        # Default mock response
        default_data = {
            "token": signer_token,
            "name": "Test Signer",
            "email": "test@example.com",
            "status": "link-opened",
            "times_viewed": 5,
            "last_view_at": datetime.now(timezone.utc).isoformat(),
            "signed_at": None,
            "sign_url": f"https://sandbox.app.zapsign.com.br/verificar/{signer_token}",
        }
        return ZapSignSignerResponse.from_api_data(default_data)

    def set_mock_signer_data(self, data: Dict[str, Any]) -> None:
        """Set mock signer data for testing."""
        self.mock_signer_data = data

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
        self.last_get_signer_call = None
        self.mock_signer_data = None