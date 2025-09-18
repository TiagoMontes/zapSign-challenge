"""Tests for AddSignerToDocumentUseCase."""

from unittest.mock import Mock
from django.test import TestCase
from core.domain.entities.signer import Signer
from core.domain.entities.document import Document
from core.domain.entities.company import Company
from core.domain.value_objects.zapsign_response import ZapSignSignerResponse
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)
from core.use_cases.signer.add_signer_to_document import (
    AddSignerToDocumentInput,
    AddSignerToDocumentOutput,
    AddSignerToDocumentUseCase,
    DocumentNotFoundError,
    DocumentAddSignerError,
    CompanyNotFoundError,
)


class TestAddSignerToDocumentUseCase(TestCase):
    def setUp(self):
        # Mock repositories
        self.mock_document_repo = Mock()
        self.mock_signer_repo = Mock()
        self.mock_company_repo = Mock()
        self.mock_zapsign_service = Mock()

        # Create use case instance
        from core.use_cases.signer.add_signer_to_document import AddSignerToDocumentUseCase
        self.use_case = AddSignerToDocumentUseCase(
            document_repository=self.mock_document_repo,
            signer_repository=self.mock_signer_repo,
            company_repository=self.mock_company_repo,
            zapsign_service=self.mock_zapsign_service
        )

        # Test data
        self.company = Company(
            id=1,
            name="Test Company",
            api_token="test-api-token"
        )

        self.document = Document(
            id=1,
            name="Test Document",
            token="doc-token-123",
            company_id=1
        )

        self.zapsign_response = ZapSignSignerResponse(
            token="new-signer-token",
            name="New Signer",
            email="new@example.com",
            status="new",
            sign_url="https://example.com/sign"
        )

    def test_add_signer_should_succeed_when_all_data_valid(self):
        """Test adding a signer to document successfully."""
        from core.use_cases.signer.add_signer_to_document import AddSignerToDocumentInput

        self.mock_document_repo.find_by_id.return_value = self.document
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.add_signer_to_document.return_value = self.zapsign_response

        new_signer = Signer(
            id=2,
            name="New Signer",
            email="new@example.com",
            token="new-signer-token",
            company_id=1,
            sign_url="https://example.com/sign",
            document_ids=[1]
        )
        self.mock_signer_repo.save.return_value = new_signer

        # Mock the refreshed signer that will be returned by find_by_id
        refreshed_signer = Signer(
            id=2,
            name="New Signer",
            email="new@example.com",
            token="new-signer-token",
            company_id=1,
            sign_url="https://example.com/sign",
            document_ids=[1]
        )
        self.mock_signer_repo.find_by_id.return_value = refreshed_signer

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer", "email": "new@example.com"}
        )

        # Act
        result: AddSignerToDocumentOutput = self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.signer.name, "New Signer")
        self.assertEqual(result.signer.email, "new@example.com")
        self.assertEqual(result.signer.token, "new-signer-token")
        self.assertEqual(result.signer.sign_url, "https://example.com/sign")
        self.assertIn(1, result.signer.document_ids)

        # Verify ZapSign API was called
        self.mock_zapsign_service.add_signer_to_document.assert_called_once_with(
            api_token="test-api-token",
            doc_token="doc-token-123",
            signer_data={"name": "New Signer", "email": "new@example.com"}
        )

        # Verify signer was saved locally
        self.mock_signer_repo.save.assert_called_once()

        # Verify M2M association was created
        self.mock_document_repo.add_signers.assert_called_once_with(1, [2])

        # Verify signer was refreshed to get updated associations
        self.mock_signer_repo.find_by_id.assert_called_once_with(2)

    def test_add_signer_should_fail_when_document_not_found(self):
        """Test adding signer when document doesn't exist."""
        from core.use_cases.signer.add_signer_to_document import (
            AddSignerToDocumentInput,
            DocumentNotFoundError
        )

        self.mock_document_repo.find_by_id.return_value = None

        input_data = AddSignerToDocumentInput(
            document_id=999,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(DocumentNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_add_signer_should_fail_when_document_has_no_token(self):
        """Test adding signer when document has no ZapSign token."""
        from core.use_cases.signer.add_signer_to_document import (
            AddSignerToDocumentInput,
            DocumentAddSignerError
        )

        document_without_token = Document(
            id=1,
            name="Test Document",
            token="",  # No token
            company_id=1
        )

        self.mock_document_repo.find_by_id.return_value = document_without_token

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(DocumentAddSignerError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_add_signer_should_fail_when_company_not_found(self):
        """Test adding signer when associated company doesn't exist."""
        from core.use_cases.signer.add_signer_to_document import (
            AddSignerToDocumentInput,
            CompanyNotFoundError
        )

        self.mock_document_repo.find_by_id.return_value = self.document
        self.mock_company_repo.find_by_id.return_value = None

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(CompanyNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_add_signer_should_propagate_zapsign_authentication_error(self):
        """Test that ZapSign authentication errors are propagated."""
        from core.use_cases.signer.add_signer_to_document import AddSignerToDocumentInput

        self.mock_document_repo.find_by_id.return_value = self.document
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.add_signer_to_document.side_effect = ZapSignAuthenticationError(
            "Authentication failed"
        )

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(ZapSignAuthenticationError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_add_signer_should_propagate_zapsign_validation_error(self):
        """Test that ZapSign validation errors are propagated."""
        from core.use_cases.signer.add_signer_to_document import AddSignerToDocumentInput

        self.mock_document_repo.find_by_id.return_value = self.document
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.add_signer_to_document.side_effect = ZapSignValidationError(
            "Validation failed"
        )

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(ZapSignValidationError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_add_signer_should_propagate_zapsign_api_error(self):
        """Test that ZapSign API errors are propagated."""
        from core.use_cases.signer.add_signer_to_document import AddSignerToDocumentInput

        self.mock_document_repo.find_by_id.return_value = self.document
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.add_signer_to_document.side_effect = ZapSignAPIError(
            "API error"
        )

        input_data = AddSignerToDocumentInput(
            document_id=1,
            signer_data={"name": "New Signer"}
        )

        with self.assertRaises(ZapSignAPIError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]