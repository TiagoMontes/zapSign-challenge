from django.test import TestCase
from unittest.mock import Mock, MagicMock
from datetime import datetime

from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.domain.entities.signer import Signer
from core.domain.value_objects.zapsign_request import (
    ZapSignDocumentRequest,
    ZapSignSignerRequest,
)
from core.domain.value_objects.zapsign_response import (
    ZapSignDocumentResponse,
    ZapSignSignerResponse,
)


class TestCreateDocumentFromUploadUseCase(TestCase):
    def setUp(self):
        from core.use_cases.document.create_document_from_upload import (
            CreateDocumentFromUploadUseCase,
        )

        self.mock_zapsign_service = Mock()
        self.mock_document_repo = Mock()
        self.mock_signer_repo = Mock()

        self.use_case = CreateDocumentFromUploadUseCase(
            zapsign_service=self.mock_zapsign_service,
            document_repository=self.mock_document_repo,
            signer_repository=self.mock_signer_repo,
        )

        self.company = Company(id=1, name="Test Company", api_token="company-api-token")

        self.zapsign_response = ZapSignDocumentResponse(
            token="doc-token-123",
            name="Test Document",
            status="pending",
            open_id=42,
            external_id="ext-doc-123",
            created_by_email="user@example.com",
            signers=[
                ZapSignSignerResponse(
                    token="signer-token-1",
                    name="John Doe",
                    status="new",
                    email="john@example.com",
                    external_id="",
                ),
                ZapSignSignerResponse(
                    token="signer-token-2",
                    name="Jane Smith",
                    status="new",
                    email="jane@example.com",
                    external_id="ext-signer-2",
                ),
            ],
        )

    def test_creates_document_with_signers_successfully(self):
        # Arrange
        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[
                ZapSignSignerRequest(name="John Doe", email="john@example.com"),
                ZapSignSignerRequest(name="Jane Smith", email="jane@example.com"),
            ],
        )

        self.mock_zapsign_service.create_document.return_value = self.zapsign_response

        created_document = Document(
            id=1,
            company_id=self.company.id,
            name="Test Document",
            token="doc-token-123",
            open_id=42,
            status="pending",
            external_id="ext-doc-123",
            created_by="user@example.com",
        )
        self.mock_document_repo.save.return_value = created_document

        created_signers = [
            Signer(
                id=1,
                name="John Doe",
                email="john@example.com",
                token="signer-token-1",
                status="new",
                external_id="",
            ),
            Signer(
                id=2,
                name="Jane Smith",
                email="jane@example.com",
                token="signer-token-2",
                status="new",
                external_id="ext-signer-2",
            ),
        ]
        self.mock_signer_repo.save_bulk.return_value = created_signers

        # Act
        result = self.use_case.execute(company=self.company, request=request)

        # Assert
        # Verify ZapSign service was called with correct parameters
        self.mock_zapsign_service.create_document.assert_called_once_with(
            api_token="company-api-token", request=request
        )

        # Verify document was saved
        self.mock_document_repo.save.assert_called_once()
        saved_doc = self.mock_document_repo.save.call_args[0][0]
        self.assertEqual(saved_doc.company_id, self.company.id)
        self.assertEqual(saved_doc.name, "Test Document")
        self.assertEqual(saved_doc.token, "doc-token-123")
        self.assertEqual(saved_doc.open_id, 42)
        self.assertEqual(saved_doc.status, "pending")
        self.assertEqual(saved_doc.external_id, "ext-doc-123")
        self.assertEqual(saved_doc.created_by, "user@example.com")

        # Verify signers were saved
        self.mock_signer_repo.save_bulk.assert_called_once()
        saved_signers = self.mock_signer_repo.save_bulk.call_args[0][0]
        self.assertEqual(len(saved_signers), 2)
        self.assertEqual(saved_signers[0].name, "John Doe")
        self.assertEqual(saved_signers[0].email, "john@example.com")
        self.assertEqual(saved_signers[0].token, "signer-token-1")
        self.assertEqual(saved_signers[1].name, "Jane Smith")
        self.assertEqual(saved_signers[1].email, "jane@example.com")
        self.assertEqual(saved_signers[1].token, "signer-token-2")

        # Verify signers were associated with document
        self.mock_document_repo.add_signers.assert_called_once_with(
            document_id=1, signer_ids=[1, 2]
        )

        # Verify result
        self.assertEqual(result.document, created_document)
        self.assertEqual(result.signers, created_signers)
        self.assertEqual(result.zapsign_response, self.zapsign_response)

    def test_handles_empty_signers_list(self):
        # Arrange
        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[],  # Empty signers list
        )

        zapsign_response = ZapSignDocumentResponse(
            token="doc-token-123",
            name="Test Document",
            status="pending",
            open_id=42,
            external_id="",
            created_by_email="user@example.com",
            signers=[],  # No signers in response
        )

        self.mock_zapsign_service.create_document.return_value = zapsign_response

        created_document = Document(
            id=1,
            company_id=self.company.id,
            name="Test Document",
            token="doc-token-123",
            open_id=42,
            status="pending",
            external_id="",
            created_by="user@example.com",
        )
        self.mock_document_repo.save.return_value = created_document

        # Act
        result = self.use_case.execute(company=self.company, request=request)

        # Assert
        self.mock_zapsign_service.create_document.assert_called_once()
        self.mock_document_repo.save.assert_called_once()
        self.mock_signer_repo.save_bulk.assert_not_called()  # No signers to save
        self.mock_document_repo.add_signers.assert_not_called()  # No signers to associate

        self.assertEqual(result.document, created_document)
        self.assertEqual(result.signers, [])
        self.assertEqual(result.zapsign_response, zapsign_response)

    def test_propagates_zapsign_service_errors(self):
        # Arrange
        from core.services.exceptions import ZapSignAuthenticationError

        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[ZapSignSignerRequest(name="John Doe")],
        )

        self.mock_zapsign_service.create_document.side_effect = ZapSignAuthenticationError(
            "Invalid API token"
        )

        # Act & Assert
        with self.assertRaises(ZapSignAuthenticationError) as context:
            self.use_case.execute(company=self.company, request=request)

        self.assertIn("Invalid API token", str(context.exception))

    def test_uses_company_api_token_for_authentication(self):
        # Arrange
        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[ZapSignSignerRequest(name="John Doe")],
        )

        self.mock_zapsign_service.create_document.return_value = self.zapsign_response
        self.mock_document_repo.save.return_value = Document(
            id=1,
            company_id=self.company.id,
            name="Test Document",
            token="doc-token-123",
            open_id=42,
            status="pending",
            external_id="",
            created_by="",
        )
        self.mock_signer_repo.save_bulk.return_value = [Mock(id=1)]

        # Act
        self.use_case.execute(company=self.company, request=request)

        # Assert - Verify the company's API token was used
        self.mock_zapsign_service.create_document.assert_called_once_with(
            api_token="company-api-token", request=request
        )