"""Service for integrating with ZapSign API."""

import requests
from typing import Dict, Any
from django.conf import settings
from requests.exceptions import RequestException, Timeout

from core.domain.value_objects.zapsign_request import ZapSignDocumentRequest
from core.domain.value_objects.zapsign_response import ZapSignDocumentResponse
from core.services.exceptions import (
    ZapSignAPIError,
    ZapSignAuthenticationError,
    ZapSignValidationError,
)


class ZapSignService:
    """Service for communicating with ZapSign API."""

    def __init__(self):
        self.base_url = settings.ZAPSIGN_API_URL
        self.timeout = 30  # seconds

    def create_document(
        self, api_token: str, request: ZapSignDocumentRequest
    ) -> ZapSignDocumentResponse:
        """
        Create a document in ZapSign API.

        Args:
            api_token: The company's API token for authentication
            request: The document creation request data

        Returns:
            ZapSignDocumentResponse with created document data

        Raises:
            ZapSignAuthenticationError: If authentication fails
            ZapSignValidationError: If request validation fails
            ZapSignAPIError: For other API errors
        """
        url = f"{self.base_url}docs/"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                json=request.to_dict(),
                headers=headers,
                timeout=self.timeout,
            )

            # Check for specific error types
            if response.status_code == 401:
                raise ZapSignAuthenticationError(
                    f"Authentication failed with ZapSign API: {self._get_error_message(response)}"
                )
            elif response.status_code == 400:
                raise ZapSignValidationError(
                    f"Validation error from ZapSign API: {self._get_error_message(response)}"
                )
            elif response.status_code >= 500:
                raise ZapSignAPIError(
                    f"Server error from ZapSign API: {self._get_error_message(response)}"
                )

            # Raise for any other non-success status codes
            response.raise_for_status()

            # Parse and return response
            data = response.json()
            return ZapSignDocumentResponse.from_api_response(data)

        except Timeout as e:
            raise ZapSignAPIError(f"Request timeout: {str(e)}")
        except RequestException as e:
            # If it's already one of our custom exceptions, re-raise it
            if isinstance(e.__cause__, (ZapSignAuthenticationError, ZapSignValidationError, ZapSignAPIError)):
                raise e.__cause__
            # Handle other request exceptions
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise ZapSignAuthenticationError(
                        f"Authentication failed with ZapSign API: {self._get_error_message(e.response)}"
                    )
                elif e.response.status_code == 400:
                    raise ZapSignValidationError(
                        f"Validation error from ZapSign API: {self._get_error_message(e.response)}"
                    )
                elif e.response.status_code >= 500:
                    raise ZapSignAPIError(
                        f"API error from ZapSign: {self._get_error_message(e.response)}"
                    )
            raise ZapSignAPIError(f"Network error: {str(e)}")
        except Exception as e:
            raise ZapSignAPIError(f"Unexpected error: {str(e)}")

    def _get_error_message(self, response) -> str:
        """Extract error message from response."""
        try:
            data = response.json()
            if isinstance(data, dict):
                return data.get("error", data.get("message", str(data)))
            return str(data)
        except:
            return response.text or f"Status code: {response.status_code}"