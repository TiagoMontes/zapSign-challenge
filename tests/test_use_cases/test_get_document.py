"""Tests for GetDocumentUseCase."""

from datetime import datetime
from django.test import TestCase
from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.use_cases.document.get_document import (
    GetDocumentUseCase,
    GetDocumentInput,
    GetDocumentOutput,
    DocumentNotFoundError,
)
from tests.fakes.document_repo import FakeDocumentRepository


class TestGetDocumentUseCase(TestCase):
    """Test cases for GetDocumentUseCase."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_repo = FakeDocumentRepository()
        self.use_case = GetDocumentUseCase(self.document_repo)

        # Create test company
        self.company = Company(
            id=1,
            name="Test Company",
            api_token="test-token",
            created_at=datetime.now(),
            last_updated_at=datetime.now(),
        )

        # Create another company for testing company isolation
        self.other_company = Company(
            id=2,
            name="Other Company",
            api_token="other-token",
            created_at=datetime.now(),
            last_updated_at=datetime.now(),
        )

    def test_get_document_should_return_document_when_exists_and_authorized(self):
        """Test getting a document that exists and belongs to the company."""
        # Arrange
        document = Document(
            company_id=1,
            name="Test Document",
            status="active",
            token="test-token",
            external_id="ext-123",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = GetDocumentInput(
            document_id=saved_document.id,
            company=self.company
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert isinstance(result, GetDocumentOutput)
        assert result.document.id == saved_document.id
        assert result.document.name == "Test Document"
        assert result.document.company_id == 1
        assert result.document.status == "active"

    def test_get_document_should_raise_error_when_document_not_found(self):
        """Test getting a document that doesn't exist."""
        # Arrange
        input_data = GetDocumentInput(
            document_id=999,  # Non-existent ID
            company=self.company
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found or not authorized" in str(context.exception)

    def test_get_document_should_raise_error_when_document_belongs_to_other_company(self):
        """Test getting a document that belongs to another company."""
        # Arrange
        document = Document(
            company_id=2,  # Belongs to other company
            name="Other Company Document",
            status="active",
            token="test-token",
            external_id="ext-456",
            created_by="other-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = GetDocumentInput(
            document_id=saved_document.id,
            company=self.company  # Company ID 1
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found or not authorized" in str(context.exception)

    def test_get_document_should_raise_error_when_document_is_soft_deleted(self):
        """Test getting a document that has been soft deleted."""
        # Arrange
        document = Document(
            company_id=1,
            name="Deleted Document",
            status="active",
            token="test-token",
            external_id="ext-789",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        # Soft delete the document
        self.document_repo.soft_delete_by_id(saved_document.id, "admin")

        input_data = GetDocumentInput(
            document_id=saved_document.id,
            company=self.company
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found or not authorized" in str(context.exception)

    def test_get_document_should_return_document_with_all_details(self):
        """Test that getting a document returns all document details correctly."""
        # Arrange
        now = datetime.now()
        document = Document(
            company_id=1,
            name="Complete Document",
            status="completed",
            token="complete-token",
            external_id="ext-complete",
            created_by="complete-user",
            open_id=12345,
            created_at=now,
            last_updated_at=now,
            signer_ids=[1, 2, 3]
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = GetDocumentInput(
            document_id=saved_document.id,
            company=self.company
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert result.document.id == saved_document.id
        assert result.document.name == "Complete Document"
        assert result.document.status == "completed"
        assert result.document.token == "complete-token"
        assert result.document.external_id == "ext-complete"
        assert result.document.created_by == "complete-user"
        assert result.document.open_id == 12345
        assert result.document.company_id == 1
        assert result.document.signer_ids == [1, 2, 3]
        assert not result.document.is_deleted