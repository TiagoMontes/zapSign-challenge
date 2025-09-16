"""Tests for DeleteDocumentWithZapSignUseCase - Simplified version without company_id requirement."""

from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from core.domain.entities.document import Document
from core.domain.entities.company import Company
from core.use_cases.document.delete_document_with_zapsign import (
    DeleteDocumentWithZapSignUseCase,
    DeleteDocumentWithZapSignInput,
    DeleteDocumentWithZapSignOutput,
    DocumentNotFoundError,
    DocumentAlreadyDeletedError,
)
from tests.fakes.document_repo import FakeDocumentRepository
from tests.fakes.company_repo import FakeCompanyRepository
from tests.fakes.zapsign_service import FakeZapSignService


class TestDeleteDocumentWithZapSignUseCase(TestCase):
    """Test cases for DeleteDocumentWithZapSignUseCase - simplified version."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_repo = FakeDocumentRepository()
        self.company_repo = FakeCompanyRepository()
        self.zapsign_service = FakeZapSignService()
        self.use_case = DeleteDocumentWithZapSignUseCase(
            self.document_repo,
            self.company_repo,
            self.zapsign_service
        )

        # Create test companies
        self.company1 = Company(
            name="Test Company 1",
            api_token="api-token-company-1",
            created_at=datetime.now(),
            last_updated_at=datetime.now(),
        )
        self.company2 = Company(
            name="Test Company 2",
            api_token="api-token-company-2",
            created_at=datetime.now(),
            last_updated_at=datetime.now(),
        )

        self.saved_company1 = self.company_repo.save(self.company1)
        self.saved_company2 = self.company_repo.save(self.company2)

    def test_delete_document_should_succeed_when_document_exists_and_has_token(self):
        """Test deleting a document that exists and has a ZapSign token."""
        # Arrange
        document = Document(
            company_id=self.saved_company1.id,
            name="Test Document",
            status="active",
            token="zapsign-token-123",
            external_id="ext-123",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = DeleteDocumentWithZapSignInput(
            document_id=saved_document.id,
            deleted_by="admin-user"
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert isinstance(result, DeleteDocumentWithZapSignOutput)
        assert result.success is True
        assert result.zapsign_deleted is True
        assert result.document.id == saved_document.id
        assert result.document.is_deleted is True
        assert result.document.deleted_by == "admin-user"
        assert result.document.deleted_at is not None

        # Verify ZapSign service was called with correct parameters
        assert self.zapsign_service.last_delete_call is not None
        assert self.zapsign_service.last_delete_call["doc_token"] == "zapsign-token-123"
        assert self.zapsign_service.last_delete_call["api_token"] == "api-token-company-1"

    def test_delete_document_should_succeed_when_document_has_no_token(self):
        """Test deleting a document that exists but has no ZapSign token."""
        # Arrange
        document = Document(
            company_id=self.saved_company1.id,
            name="Local Document",
            status="active",
            token="",  # No ZapSign token
            external_id="ext-456",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = DeleteDocumentWithZapSignInput(
            document_id=saved_document.id,
            deleted_by="admin-user"
        )

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert isinstance(result, DeleteDocumentWithZapSignOutput)
        assert result.success is True
        assert result.zapsign_deleted is False  # No token, so no ZapSign deletion
        assert result.document.id == saved_document.id
        assert result.document.is_deleted is True
        assert result.document.deleted_by == "admin-user"
        assert result.document.deleted_at is not None

        # Verify ZapSign service was not called
        assert self.zapsign_service.last_delete_call is None

    def test_delete_document_should_raise_error_when_document_not_found(self):
        """Test deleting a document that doesn't exist."""
        # Arrange
        input_data = DeleteDocumentWithZapSignInput(
            document_id=999,  # Non-existent ID
            deleted_by="admin-user"
        )

        # Act & Assert
        with self.assertRaises(DocumentNotFoundError) as context:
            self.use_case.execute(input_data)

        assert "Document not found" in str(context.exception)

    def test_delete_document_should_raise_error_when_document_already_deleted(self):
        """Test deleting a document that is already soft deleted."""
        # Arrange
        document = Document(
            company_id=self.saved_company1.id,
            name="Already Deleted Document",
            status="active",
            token="test-token",
            external_id="ext-789",
            created_by="test-user"
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        # First deletion
        first_input = DeleteDocumentWithZapSignInput(
            document_id=saved_document.id,
            deleted_by="first-admin"
        )
        self.use_case.execute(first_input)

        # Second deletion attempt
        second_input = DeleteDocumentWithZapSignInput(
            document_id=saved_document.id,
            deleted_by="second-admin"
        )

        # Act & Assert
        with self.assertRaises(DocumentAlreadyDeletedError) as context:
            self.use_case.execute(second_input)

        assert "Document is already deleted" in str(context.exception)

    def test_delete_document_should_work_regardless_of_company(self):
        """Test that document deletion works for any company when given just document_id."""
        # Arrange - Create documents from different companies
        doc1 = Document(
            company_id=self.saved_company1.id,
            name="Company 1 Document",
            status="active",
            token="token-1",
            external_id="ext-1",
            created_by="user1"
        )
        doc2 = Document(
            company_id=self.saved_company2.id,
            name="Company 2 Document",
            status="active",
            token="token-2",
            external_id="ext-2",
            created_by="user2"
        )

        saved_doc1 = self.document_repo.save(doc1)
        saved_doc2 = self.document_repo.save(doc2)
        assert saved_doc1.id is not None, "Saved document should have an ID"
        assert saved_doc2.id is not None, "Saved document should have an ID"

        # Act - Delete documents from different companies using only document_id
        input1 = DeleteDocumentWithZapSignInput(
            document_id=saved_doc1.id,
            deleted_by="admin"
        )
        input2 = DeleteDocumentWithZapSignInput(
            document_id=saved_doc2.id,
            deleted_by="admin"
        )

        result1 = self.use_case.execute(input1)
        result2 = self.use_case.execute(input2)

        # Assert - Both deletions should succeed
        assert result1.success is True
        assert result1.document.company_id == self.saved_company1.id
        assert result1.document.is_deleted is True

        assert result2.success is True
        assert result2.document.company_id == self.saved_company2.id
        assert result2.document.is_deleted is True

    def test_delete_document_should_preserve_audit_information(self):
        """Test that deleting a document preserves all audit information."""
        # Arrange
        original_time = timezone.now()
        document = Document(
            company_id=self.saved_company1.id,
            name="Audit Test Document",
            status="completed",
            token="audit-token",
            external_id="ext-audit",
            created_by="original-user",
            created_at=original_time,
            last_updated_at=original_time
        )
        saved_document = self.document_repo.save(document)
        assert saved_document.id is not None, "Saved document should have an ID"

        input_data = DeleteDocumentWithZapSignInput(
            document_id=saved_document.id,
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