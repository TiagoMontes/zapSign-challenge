from datetime import datetime, timezone
from django.test import TestCase
from api.serializers.document import DocumentSerializer, DocumentSimpleSerializer
from core.domain.entities.document import Document
from core.domain.entities.company import Company
from core.domain.entities.signer import Signer


class TestDocumentSerializer(TestCase):
    """Test suite for DocumentSerializer."""

    def test_document_serializer_should_include_company_id_field_when_serializing_entity(self):
        """Test that DocumentSerializer includes company_id field in serialized output."""
        # Arrange - Create a document entity with company_id
        document = Document(
            id=1,
            company_id=10,
            name="Test Document",
            status="draft",
            token="test-token",
            created_by="user@example.com",
            external_id="ext-123",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # Mock empty signers list for serialization
        document.signers = []

        # Act - Serialize the document
        serializer = DocumentSerializer(document)
        data = serializer.data

        # Assert - Should include company_id field
        assert "company_id" in data
        assert data["company_id"] == 10

    def test_document_serializer_should_handle_nested_company_data_correctly(self):
        """Test that DocumentSerializer properly handles company data when available."""
        # Arrange - Create a document with related data
        company = Company(
            id=10,
            name="Test Company",
            api_token="test-api-token",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        signers = [
            Signer(
                id=1,
                name="John Doe",
                email="john@example.com",
                token="signer-token-1",
                status="pending",
                external_id="signer-ext-1",
            )
        ]

        document = Document(
            id=1,
            company_id=10,
            name="Test Document",
            status="draft",
            token="test-token",
            created_by="user@example.com",
            external_id="ext-123",
            signer_ids=[1],
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # Mock the document with company and signers attributes for serialization
        # Note: In real usage, this would be handled by the repository layer
        document.company = company
        document.signers = signers

        # Act - Serialize the document
        serializer = DocumentSerializer(document)
        data = serializer.data

        # Assert - Should include company_id matching the nested company.id
        assert data["company_id"] == 10
        assert data["company"]["id"] == 10
        assert data["company"]["name"] == "Test Company"

    def test_document_serializer_should_handle_missing_company_data_gracefully(self):
        """Test that DocumentSerializer handles missing company data gracefully."""
        # Arrange - Create a document without company attribute (typical repository result)
        document = Document(
            id=1,
            company_id=10,
            name="Test Document",
            status="draft",
            token="test-token",
            created_by="user@example.com",
            external_id="ext-123",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # Mock empty signers list for serialization
        document.signers = []

        # Act - Serialize the document
        serializer = DocumentSerializer(document)
        data = serializer.data

        # Assert - Should include company_id but company should be None
        assert data["company_id"] == 10
        assert data["company"] is None

    def test_document_simple_serializer_should_include_company_id_field(self):
        """Test that DocumentSimpleSerializer also includes company_id field."""
        # Arrange - Create a document entity
        document = Document(
            id=1,
            company_id=15,
            name="Simple Test Document",
            status="pending",
            token="simple-token",
            created_by="user@example.com",
            external_id="simple-ext-123",
            signer_ids=[1, 2],
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # Mock signers for serialization
        document.signers = [
            Signer(
                id=1,
                name="Signer One",
                email="signer1@example.com",
                token="token1",
                status="pending",
                external_id="ext1",
            ),
            Signer(
                id=2,
                name="Signer Two",
                email="signer2@example.com",
                token="token2",
                status="pending",
                external_id="ext2",
            ),
        ]

        # Act - Serialize with DocumentSimpleSerializer
        serializer = DocumentSimpleSerializer(document)
        data = serializer.data

        # Assert - Should include company_id
        assert "company_id" in data
        assert data["company_id"] == 15
        # Should NOT include company object (this is the "simple" version)
        assert "company" not in data

    def test_document_serializer_should_preserve_all_existing_fields(self):
        """Test that adding company_id doesn't break existing field serialization."""
        # Arrange - Create a complete document entity
        document = Document(
            id=100,
            company_id=25,
            name="Complete Document",
            status="completed",
            token="complete-token",
            open_id=500,
            created_by="admin@example.com",
            external_id="complete-ext-123",
            signer_ids=[],
            created_at=datetime(2023, 6, 15, 14, 30, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 6, 16, 10, 15, 0, tzinfo=timezone.utc),
            # PDF processing fields
            url_pdf="https://example.com/document.pdf",
            processing_status="INDEXED",
            checksum="abc123def456",
            version_id="v1.0.0",
        )

        # Mock company and empty signers
        document.company = Company(
            id=25,
            name="Complete Company",
            api_token="complete-api-token",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            last_updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        document.signers = []

        # Act - Serialize the document
        serializer = DocumentSerializer(document)
        data = serializer.data

        # Assert - All fields should be present and correct
        assert data["id"] == 100
        assert data["company_id"] == 25
        assert data["name"] == "Complete Document"
        assert data["status"] == "completed"
        assert data["token"] == "complete-token"
        assert data["open_id"] == 500
        assert data["created_by"] == "admin@example.com"
        assert data["external_id"] == "complete-ext-123"
        assert data["url_pdf"] == "https://example.com/document.pdf"
        assert data["processing_status"] == "INDEXED"
        assert data["checksum"] == "abc123def456"
        assert data["version_id"] == "v1.0.0"
        assert data["company"]["id"] == 25
        assert data["company"]["name"] == "Complete Company"
        assert data["signers"] == []