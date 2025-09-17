"""Test to debug signers and sign_url issues in document creation."""

from django.test import TestCase
from unittest.mock import Mock, patch
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
from core.use_cases.document.create_document_from_upload import CreateDocumentFromUploadUseCase
from core.repositories.document_repo import DjangoDocumentRepository
from core.repositories.signer_repo import DjangoSignerRepository
from core.orm.models import Company as CompanyModel, Document as DocumentModel, Signer as SignerModel


class TestSignersDebugIssue(TestCase):
    """Test to reproduce and debug the signers issues."""

    def setUp(self):
        """Set up test data."""
        # Create a real company in the database
        self.company_model = CompanyModel.objects.create(
            name="Test Company",
            api_token="test-api-token-123"
        )
        self.company = Company(
            id=self.company_model.id,
            name="Test Company",
            api_token="test-api-token-123"
        )

        # Real repositories
        self.document_repo = DjangoDocumentRepository()
        self.signer_repo = DjangoSignerRepository()

    def test_sign_url_is_saved_from_zapsign_response(self):
        """Test that sign_url from ZapSign response is properly saved to database."""
        # Create mock ZapSign response with sign_url
        zapsign_response = ZapSignDocumentResponse(
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
                    external_id="ext-signer-1",
                    sign_url="https://sandbox.app.zapsign.com.br/verificar/signer-1-url",
                ),
                ZapSignSignerResponse(
                    token="signer-token-2",
                    name="Jane Smith",
                    status="new",
                    email="jane@example.com",
                    external_id="ext-signer-2",
                    sign_url="https://sandbox.app.zapsign.com.br/verificar/signer-2-url",
                ),
            ],
        )

        # Mock ZapSign service
        mock_zapsign_service = Mock()
        mock_zapsign_service.create_document.return_value = zapsign_response

        # Mock PDF service
        mock_pdf_service = Mock()
        mock_pdf_service.download_and_extract_text.return_value = ("extracted text", "abc123")

        # Create use case with real repositories
        use_case = CreateDocumentFromUploadUseCase(
            zapsign_service=mock_zapsign_service,
            document_repository=self.document_repo,
            signer_repository=self.signer_repo,
            pdf_service=mock_pdf_service,
        )

        # Execute use case
        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[
                ZapSignSignerRequest(name="John Doe", email="john@example.com"),
                ZapSignSignerRequest(name="Jane Smith", email="jane@example.com"),
            ],
        )

        result = use_case.execute(company=self.company, request=request)

        # Verify document was created
        self.assertIsNotNone(result.document.id)

        # Verify signers were created and saved to database
        self.assertEqual(len(result.signers), 2)

        # Check that signers have sign_url
        for signer in result.signers:
            self.assertIsNotNone(signer.id, "Signer should have an ID after saving")
            self.assertNotEqual(signer.sign_url, "", f"Signer {signer.name} should have a sign_url")

        # Verify data is actually in the database
        saved_signers = SignerModel.objects.filter(
            documents__id=result.document.id
        ).all()

        self.assertEqual(len(saved_signers), 2, "Two signers should be in the database")

        # Check sign_url in database
        signer_names_and_urls = [(s.name, s.sign_url) for s in saved_signers]
        print(f"[DEBUG] Signers in DB: {signer_names_and_urls}")

        for signer_model in saved_signers:
            self.assertNotEqual(signer_model.sign_url, "",
                              f"Signer {signer_model.name} should have sign_url in DB")

    def test_document_retrieval_includes_signers_with_sign_url(self):
        """Test that retrieving a document includes signers with sign_url."""
        # First create a document with signers
        self.test_sign_url_is_saved_from_zapsign_response()

        # Get the document ID from database
        document_model = DocumentModel.objects.filter(
            company_id=self.company.id
        ).first()

        self.assertIsNotNone(document_model, "Document should exist in database")

        # Retrieve document using repository
        retrieved_document = self.document_repo.find_by_id(document_model.id)

        self.assertIsNotNone(retrieved_document, "Retrieved document should not be None")
        self.assertIsNotNone(retrieved_document.signers, "Document should have signers")
        self.assertGreater(len(retrieved_document.signers), 0, "Document should have at least 1 signer")

        # Verify signers have sign_url
        for signer in retrieved_document.signers:
            print(f"[DEBUG] Retrieved signer: {signer.name}, sign_url: {signer.sign_url}")
            self.assertNotEqual(signer.sign_url, "",
                              f"Retrieved signer {signer.name} should have sign_url")