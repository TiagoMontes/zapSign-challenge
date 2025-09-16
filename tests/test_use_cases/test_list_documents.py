"""Tests for ListDocumentsUseCase."""

from datetime import datetime
from django.test import TestCase
from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.use_cases.document.list_documents import (
    ListDocumentsUseCase,
    ListDocumentsInput,
    ListDocumentsOutput,
)
from tests.fakes.document_repo import FakeDocumentRepository


class TestListDocumentsUseCase(TestCase):
    """Test cases for ListDocumentsUseCase."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_repo = FakeDocumentRepository()
        self.use_case = ListDocumentsUseCase(self.document_repo)

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

    def test_list_documents_should_return_empty_list_when_no_documents_exist(self):
        """Test listing documents when no documents exist."""
        # Arrange
        input_data = ListDocumentsInput(company=self.company)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert isinstance(result, ListDocumentsOutput)
        assert result.documents == []
        assert result.total_count == 0
        assert result.page == 1
        assert result.page_size == 10
        assert result.has_next is False
        assert result.has_previous is False

    def test_list_documents_should_return_company_documents_only_when_documents_exist(self):
        """Test listing documents returns only documents for the specified company."""
        # Arrange
        doc1 = Document(company_id=1, name="Company 1 Doc 1")
        doc2 = Document(company_id=1, name="Company 1 Doc 2")
        doc3 = Document(company_id=2, name="Company 2 Doc 1")

        self.document_repo.save(doc1)
        self.document_repo.save(doc2)
        self.document_repo.save(doc3)

        input_data = ListDocumentsInput(company=self.company)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 2
        assert result.total_count == 2
        # Documents should be ordered by ID descending (newest first)
        assert result.documents[0].name == "Company 1 Doc 2"
        assert result.documents[1].name == "Company 1 Doc 1"
        assert all(doc.company_id == 1 for doc in result.documents)

    def test_list_documents_should_exclude_deleted_documents_by_default(self):
        """Test listing documents excludes soft deleted documents by default."""
        # Arrange
        doc1 = Document(company_id=1, name="Active Doc")
        doc2 = Document(company_id=1, name="Deleted Doc")

        saved_doc1 = self.document_repo.save(doc1)
        saved_doc2 = self.document_repo.save(doc2)
        assert saved_doc2.id is not None, "Saved document should have an ID"

        # Soft delete one document
        self.document_repo.soft_delete_by_id(saved_doc2.id, "test_user")

        input_data = ListDocumentsInput(company=self.company)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 1
        assert result.total_count == 1
        assert result.documents[0].name == "Active Doc"

    def test_list_documents_should_include_deleted_documents_when_requested(self):
        """Test listing documents includes soft deleted documents when explicitly requested."""
        # Arrange
        doc1 = Document(company_id=1, name="Active Doc")
        doc2 = Document(company_id=1, name="Deleted Doc")

        saved_doc1 = self.document_repo.save(doc1)
        saved_doc2 = self.document_repo.save(doc2)
        assert saved_doc2.id is not None, "Saved document should have an ID"

        # Soft delete one document
        self.document_repo.soft_delete_by_id(saved_doc2.id, "test_user")

        input_data = ListDocumentsInput(company=self.company, include_deleted=True)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 2
        assert result.total_count == 2
        document_names = [doc.name for doc in result.documents]
        assert "Active Doc" in document_names
        assert "Deleted Doc" in document_names

    def test_list_documents_should_implement_pagination_correctly(self):
        """Test listing documents implements pagination correctly."""
        # Arrange - Create 15 documents to test pagination
        for i in range(15):
            doc = Document(company_id=1, name=f"Document {i+1}")
            self.document_repo.save(doc)

        # Test first page
        input_data = ListDocumentsInput(company=self.company, page=1, page_size=5)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 5
        assert result.total_count == 15
        assert result.page == 1
        assert result.page_size == 5
        assert result.has_next is True
        assert result.has_previous is False
        # Should have newest documents first (Document 15, 14, 13, 12, 11)
        assert result.documents[0].name == "Document 15"
        assert result.documents[4].name == "Document 11"

    def test_list_documents_should_handle_second_page_correctly(self):
        """Test listing documents handles second page correctly."""
        # Arrange - Create 15 documents
        for i in range(15):
            doc = Document(company_id=1, name=f"Document {i+1}")
            self.document_repo.save(doc)

        # Test second page
        input_data = ListDocumentsInput(company=self.company, page=2, page_size=5)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 5
        assert result.total_count == 15
        assert result.page == 2
        assert result.page_size == 5
        assert result.has_next is True
        assert result.has_previous is True
        # Should have next 5 documents (Document 10, 9, 8, 7, 6)
        assert result.documents[0].name == "Document 10"
        assert result.documents[4].name == "Document 6"

    def test_list_documents_should_handle_last_page_correctly(self):
        """Test listing documents handles last page correctly."""
        # Arrange - Create 12 documents
        for i in range(12):
            doc = Document(company_id=1, name=f"Document {i+1}")
            self.document_repo.save(doc)

        # Test last page (page 3 with page_size 5)
        input_data = ListDocumentsInput(company=self.company, page=3, page_size=5)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 2  # Only 2 documents on last page
        assert result.total_count == 12
        assert result.page == 3
        assert result.page_size == 5
        assert result.has_next is False
        assert result.has_previous is True
        # Should have the last 2 documents (Document 2, 1)
        assert result.documents[0].name == "Document 2"
        assert result.documents[1].name == "Document 1"

    def test_list_documents_should_handle_empty_page_gracefully(self):
        """Test listing documents handles empty page gracefully."""
        # Arrange - Create 5 documents
        for i in range(5):
            doc = Document(company_id=1, name=f"Document {i+1}")
            self.document_repo.save(doc)

        # Request page beyond available data
        input_data = ListDocumentsInput(company=self.company, page=10, page_size=5)

        # Act
        result = self.use_case.execute(input_data)

        # Assert
        assert len(result.documents) == 0
        assert result.total_count == 5
        assert result.page == 10
        assert result.page_size == 5
        assert result.has_next is False
        assert result.has_previous is True