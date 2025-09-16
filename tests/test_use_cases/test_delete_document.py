"""Tests for SoftDeleteDocumentUseCase."""

from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.use_cases.document.delete_document import (
    SoftDeleteDocumentUseCase,
    DeleteDocumentInput,
    DeleteDocumentOutput,
    DocumentNotFoundError,
    DocumentAlreadyDeletedError,
)
from tests.fakes.document_repo import FakeDocumentRepository


class TestSoftDeleteDocumentUseCase(TestCase):
    """Test cases for SoftDeleteDocumentUseCase."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_repo = FakeDocumentRepository()
        self.use_case = SoftDeleteDocumentUseCase(self.document_repo)

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

    def test_soft_delete_document_should_mark_document_as_deleted_when_authorized(self):
        """Test soft deleting a document that exists and belongs to the company."""
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

        input_data = DeleteDocumentInput(
            document_id=saved_document.id,
            company=self.company,
            deleted_by="admin-user"
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert isinstance(result, DeleteDocumentOutput)
        assert result.success is True
        assert result.document.id == saved_document.id
        assert result.document.is_deleted is True
        assert result.document.deleted_by == "admin-user"
        assert result.document.deleted_at is not None

        # Verify document is actually marked as deleted in repository
        retrieved_document = self.document_repo.find_by_id(saved_document.id)
        assert retrieved_document is not None
        assert retrieved_document.is_deleted is True

    def test_soft_delete_document_should_raise_error_when_document_not_found(self):
        """Test soft deleting a document that doesn't exist."""
        # Arrange
        input_data = DeleteDocumentInput(
            document_id=999,  # Non-existent ID
            company=self.company,
            deleted_by="admin-user"
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found or not authorized" in str(context.exception)

    def test_soft_delete_document_should_raise_error_when_document_belongs_to_other_company(self):
        """Test soft deleting a document that belongs to another company."""
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

        input_data = DeleteDocumentInput(
            document_id=saved_document.id,
            company=self.company,  # Company ID 1
            deleted_by="admin-user"
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found or not authorized" in str(context.exception)

    def test_soft_delete_document_should_raise_error_when_document_already_deleted(self):
        """Test soft deleting a document that is already soft deleted."""
        # Arrange
        document = Document(
            company_id=1,
            name="Already Deleted Document",
            status="active",
            token="test-token",
            external_id="ext-789",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)

        # First deletion
        first_input = DeleteDocumentInput(
            document_id=saved_document.id,
            company=self.company,
            deleted_by="first-admin"
        )
        self.use_case.execute(first_input)

        # Second deletion attempt
        second_input = DeleteDocumentInput(
            document_id=saved_document.id,
            company=self.company,
            deleted_by="second-admin"
        )

        # Act & Assert
        with self.assertRaises(DocumentAlreadyDeletedError) as context:
            self.use_case.execute(second_input)

        assert "Document is already deleted" in str(context.exception)

    def test_soft_delete_document_should_preserve_audit_information(self):
        """Test that soft deleting a document preserves all audit information."""
        # Arrange
        original_time = timezone.now()
        document = Document(
            company_id=1,
            name="Audit Test Document",
            status="completed",
            token="audit-token",
            external_id="ext-audit",
            created_by="original-user",
            created_at=original_time,
            last_updated_at=original_time
        )
        saved_document = self.document_repo.save(document)

        input_data = DeleteDocumentInput(
            document_id=saved_document.id,
            company=self.company,
            deleted_by="audit-admin"
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert - Check that all original data is preserved
        assert result.document.name == "Audit Test Document"
        assert result.document.status == "completed"
        assert result.document.token == "audit-token"
        assert result.document.external_id == "ext-audit"
        assert result.document.created_by == "original-user"
        assert result.document.created_at == original_time
        assert result.document.last_updated_at == original_time

        # Assert - Check that soft delete audit fields are set
        assert result.document.is_deleted is True
        assert result.document.deleted_by == "audit-admin"
        assert result.document.deleted_at is not None
        assert result.document.deleted_at >= original_time

    def test_soft_delete_document_should_not_affect_other_documents(self):
        """Test that soft deleting one document doesn't affect others."""
        # Arrange
        doc1 = Document(company_id=1, name="Document 1", created_by="user1")
        doc2 = Document(company_id=1, name="Document 2", created_by="user2")
        doc3 = Document(company_id=2, name="Document 3", created_by="user3")

        saved_doc1 = self.document_repo.save(doc1)
        saved_doc2 = self.document_repo.save(doc2)
        saved_doc3 = self.document_repo.save(doc3)

        input_data = DeleteDocumentInput(
            document_id=saved_doc1.id,
            company=self.company,
            deleted_by="admin"
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert result.document.id == saved_doc1.id
        assert result.document.is_deleted is True

        # Check other documents are not affected
        remaining_doc2 = self.document_repo.find_by_id(saved_doc2.id)
        remaining_doc3 = self.document_repo.find_by_id(saved_doc3.id)

        assert remaining_doc2 is not None
        assert remaining_doc2.is_deleted is False
        assert remaining_doc3 is not None
        assert remaining_doc3.is_deleted is False