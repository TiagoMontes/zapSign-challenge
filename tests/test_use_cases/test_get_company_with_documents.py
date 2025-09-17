from django.test import TestCase
from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.use_cases.company.get_company_with_documents import (
    GetCompanyWithDocuments,
    GetCompanyWithDocumentsInput,
    CompanyWithDocuments
)
from core.use_cases.company.exceptions import CompanyNotFoundError
from tests.fakes.company_repo import FakeCompanyRepository
from tests.fakes.document_repo import FakeDocumentRepository


class TestGetCompanyWithDocumentsUseCase(TestCase):
    """Test Get Company With Documents use case."""

    def setUp(self):
        """Set up test data."""
        self.company_repository = FakeCompanyRepository()
        self.document_repository = FakeDocumentRepository()
        self.use_case = GetCompanyWithDocuments(self.company_repository, self.document_repository)

    def test_execute_should_return_company_with_empty_documents_when_no_documents_exist(self):
        """Test that execute returns company with empty documents list when company has no documents."""
        # Create company without documents
        company = Company(id=1, name="Test Company", api_token="test-token")
        self.company_repository.save(company)

        input_data = GetCompanyWithDocumentsInput(company_id=1)
        result = self.use_case.execute(input_data)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, CompanyWithDocuments)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "test-token")
        self.assertEqual(len(result.documents), 0)

    def test_execute_should_return_company_with_documents_when_documents_exist(self):
        """Test that execute returns company with documents when they exist."""
        # Create company
        company = Company(id=1, name="Test Company", api_token="test-token")
        self.company_repository.save(company)

        # Create documents for this company
        doc1 = Document(id=1, company_id=1, name="Contract ABC", status="pending")
        doc2 = Document(id=2, company_id=1, name="Agreement XYZ", status="signed")
        self.document_repository.save(doc1)
        self.document_repository.save(doc2)

        input_data = GetCompanyWithDocumentsInput(company_id=1)
        result = self.use_case.execute(input_data)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, CompanyWithDocuments)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "test-token")
        self.assertEqual(len(result.documents), 2)

        # Check documents are in the response (order might vary, so check both exist)
        document_names = [doc.name for doc in result.documents]
        document_statuses = [doc.status for doc in result.documents]
        self.assertIn("Contract ABC", document_names)
        self.assertIn("Agreement XYZ", document_names)
        self.assertIn("pending", document_statuses)
        self.assertIn("signed", document_statuses)

    def test_execute_should_exclude_soft_deleted_documents(self):
        """Test that execute excludes soft deleted documents."""
        # Create company
        company = Company(id=1, name="Test Company", api_token="test-token")
        self.company_repository.save(company)

        # Create documents - one active, one soft deleted
        doc1 = Document(id=1, company_id=1, name="Active Doc", status="pending")
        doc2 = Document(id=2, company_id=1, name="Deleted Doc", status="signed")
        doc2.soft_delete("test_user")  # Soft delete this document

        self.document_repository.save(doc1)
        self.document_repository.save(doc2)

        input_data = GetCompanyWithDocumentsInput(company_id=1)
        result = self.use_case.execute(input_data)

        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].name, "Active Doc")

    def test_execute_should_only_return_documents_for_specified_company(self):
        """Test that execute only returns documents belonging to the specified company."""
        # Create two companies
        company1 = Company(id=1, name="Company 1", api_token="token-1")
        company2 = Company(id=2, name="Company 2", api_token="token-2")
        self.company_repository.save(company1)
        self.company_repository.save(company2)

        # Create documents for both companies
        doc1 = Document(id=1, company_id=1, name="Doc for Company 1", status="pending")
        doc2 = Document(id=2, company_id=2, name="Doc for Company 2", status="signed")
        self.document_repository.save(doc1)
        self.document_repository.save(doc2)

        # Request company 1 with documents
        input_data = GetCompanyWithDocumentsInput(company_id=1)
        result = self.use_case.execute(input_data)

        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].name, "Doc for Company 1")

    def test_execute_should_raise_error_when_company_not_found(self):
        """Test that execute raises error when company is not found."""
        input_data = GetCompanyWithDocumentsInput(company_id=999)

        with self.assertRaises(CompanyNotFoundError) as cm:
            self.use_case.execute(input_data)

        self.assertIn("Company with ID 999 not found", str(cm.exception))

    def test_company_with_documents_from_company_should_create_correct_structure(self):
        """Test CompanyWithDocuments.from_company creates correct structure."""
        from datetime import datetime

        # Create company with datetime fields
        company = Company(
            id=1,
            name="Test Company",
            api_token="test-token",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            last_updated_at=datetime(2023, 1, 2, 12, 0, 0)
        )

        # Create documents
        documents = [
            Document(id=1, company_id=1, name="Doc 1", status="pending"),
            Document(id=2, company_id=1, name="Doc 2", status="signed")
        ]

        result = CompanyWithDocuments.from_company(company, documents)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "test-token")
        self.assertEqual(result.created_at, "2023-01-01T12:00:00")
        self.assertEqual(result.last_updated_at, "2023-01-02T12:00:00")
        self.assertEqual(len(result.documents), 2)