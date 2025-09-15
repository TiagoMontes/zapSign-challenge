from unittest.mock import Mock, patch
from django.test import TestCase
from requests.exceptions import RequestException, Timeout
from core.domain.value_objects.zapsign_request import (
    ZapSignDocumentRequest,
    ZapSignSignerRequest,
)


class TestZapSignService(TestCase):
    def setUp(self):
        from core.services.zapsign_service import ZapSignService
        self.service = ZapSignService()

    def get_mock_response(self):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {
            "sandbox": False,
            "external_id": "doc-123",
            "open_id": 2,
            "token": "934f3d4b-eece-43bc-b4d1-04599ad2f9aa",
            "name": "My PDF Contract",
            "status": "pending",
            "created_by": {"email": "user@example.com"},
            "created_at": "2025-09-15T16:14:52.542260Z",
            "last_update_at": "2025-09-15T16:14:52.542277Z",
            "signers": [
                {
                    "external_id": "",
                    "sign_url": "https://sandbox.app.zapsign.com.br/verificar/adb099fc",
                    "token": "adb099fc-9f2f-4774-a263-de1aea884f75",
                    "status": "new",
                    "name": "John Doe",
                    "email": "",
                },
            ],
        }
        return mock

    def test_create_document_success(self):
        mock_response = self.get_mock_response()
        with patch("requests.post", return_value=mock_response) as mock_post:
            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document",
                url_pdf="https://example.com/doc.pdf",
                signers=[signer],
            )

            response = self.service.create_document(api_token="test-token", request=request)

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Check URL
            self.assertIn("https://sandbox.api.zapsign.com.br/api/v1/docs/", call_args[0][0])

            # Check headers
            headers = call_args[1]["headers"]
            self.assertEqual(headers["Authorization"], "Bearer test-token")
            self.assertEqual(headers["Content-Type"], "application/json")

            # Check response
            self.assertEqual(response.token, "934f3d4b-eece-43bc-b4d1-04599ad2f9aa")
            self.assertEqual(response.name, "My PDF Contract")
            self.assertEqual(response.status, "pending")
            self.assertEqual(len(response.signers), 1)

    def test_create_document_with_authentication_error(self):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_response.raise_for_status.side_effect = RequestException("401 Unauthorized")

        with patch("requests.post", return_value=mock_response):
            from core.services.exceptions import ZapSignAPIError

            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document",
                url_pdf="https://example.com/doc.pdf",
                signers=[signer],
            )

            with self.assertRaises(ZapSignAPIError) as context:
                self.service.create_document(api_token="invalid-token", request=request)

            self.assertIn("Authentication failed", str(context.exception))

    def test_create_document_with_validation_error(self):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "Invalid request",
            "details": "URL PDF is required",
        }
        mock_response.raise_for_status.side_effect = RequestException("400 Bad Request")

        with patch("requests.post", return_value=mock_response):
            from core.services.exceptions import ZapSignAPIError

            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document", url_pdf="", signers=[signer]
            )

            with self.assertRaises(ZapSignAPIError) as context:
                self.service.create_document(api_token="test-token", request=request)

            self.assertIn("Validation error", str(context.exception))

    def test_create_document_with_server_error(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = RequestException("500 Server Error")

        with patch("requests.post", return_value=mock_response):
            from core.services.exceptions import ZapSignAPIError

            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document",
                url_pdf="https://example.com/doc.pdf",
                signers=[signer],
            )

            with self.assertRaises(ZapSignAPIError) as context:
                self.service.create_document(api_token="test-token", request=request)

            self.assertIn("Server error", str(context.exception))

    def test_create_document_with_timeout(self):
        with patch("requests.post", side_effect=Timeout("Request timeout")):
            from core.services.exceptions import ZapSignAPIError

            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document",
                url_pdf="https://example.com/doc.pdf",
                signers=[signer],
            )

            with self.assertRaises(ZapSignAPIError) as context:
                self.service.create_document(api_token="test-token", request=request)

            self.assertIn("Request timeout", str(context.exception))

    def test_create_document_with_network_error(self):
        with patch(
            "requests.post", side_effect=RequestException("Network connection failed")
        ):
            from core.services.exceptions import ZapSignAPIError

            signer = ZapSignSignerRequest(name="John Doe")
            request = ZapSignDocumentRequest(
                name="Test Document",
                url_pdf="https://example.com/doc.pdf",
                signers=[signer],
            )

            with self.assertRaises(ZapSignAPIError) as context:
                self.service.create_document(api_token="test-token", request=request)

            self.assertIn("Network error", str(context.exception))

    def test_uses_correct_api_url_from_settings(self):
        mock_response = self.get_mock_response()
        with patch("requests.post", return_value=mock_response) as mock_post:
            with patch(
                "core.services.zapsign_service.settings.ZAPSIGN_API_URL",
                "https://custom.api.url/v2/",
            ):
                from core.services.zapsign_service import ZapSignService

                custom_service = ZapSignService()

                signer = ZapSignSignerRequest(name="John Doe")
                request = ZapSignDocumentRequest(
                    name="Test Document",
                    url_pdf="https://example.com/doc.pdf",
                    signers=[signer],
                )

                custom_service.create_document(api_token="test-token", request=request)

                call_args = mock_post.call_args
                self.assertIn("https://custom.api.url/v2/docs/", call_args[0][0])