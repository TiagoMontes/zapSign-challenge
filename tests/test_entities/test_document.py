"""Tests for Document entity."""

import unittest
from datetime import datetime, timezone
from core.domain.entities.document import Document
from core.domain.entities.signer import Signer


class TestDocument(unittest.TestCase):
    """Test cases for Document entity."""

    def test_document_should_require_company_id_when_created(self) -> None:
        """Test that Document requires company_id."""
        with self.assertRaisesRegex(ValueError, "Document.company_id is required"):
            Document(name="Test Document")

    def test_document_should_require_name_when_created(self) -> None:
        """Test that Document requires a non-empty name."""
        with self.assertRaisesRegex(ValueError, "Document.name must not be empty"):
            Document(company_id=1, name="")

        with self.assertRaisesRegex(ValueError, "Document.name must not be empty"):
            Document(company_id=1, name="   ")

    def test_document_should_allow_valid_creation(self) -> None:
        """Test that Document can be created with valid data."""
        doc = Document(company_id=1, name="Valid Document")
        self.assertEqual(doc.company_id, 1)
        self.assertEqual(doc.name, "Valid Document")
        self.assertTrue(doc.is_active())

    def test_document_should_soft_delete_with_pure_python_datetime(self) -> None:
        """Test that Document can be soft deleted without Django dependencies."""
        # This test verifies that the entity uses pure Python datetime
        doc = Document(company_id=1, name="Test Document")
        deleted_by = "test_user"

        doc.soft_delete(deleted_by)

        self.assertTrue(doc.is_deleted)
        self.assertEqual(doc.deleted_by, deleted_by)
        self.assertIsNotNone(doc.deleted_at)
        self.assertIsInstance(doc.deleted_at, datetime)
        # Should use UTC timezone (not Django's timezone.now() which uses aware datetime)
        if doc.deleted_at is not None:
            self.assertEqual(doc.deleted_at.tzinfo, timezone.utc)
            self.assertFalse(doc.is_active())

            # Additional check: ensure we're not using Django timezone
            # Django timezone.now() would give timezone-aware datetime but might not be UTC
            # We want to ensure this is pure Python UTC
            from datetime import datetime as dt
            now_utc = dt.now(timezone.utc)
            # The deleted_at should be close to now (within 1 second)
            time_diff = abs((doc.deleted_at - now_utc).total_seconds())
            self.assertLess(time_diff, 1.0)

    def test_document_should_not_allow_double_soft_delete(self) -> None:
        """Test that Document cannot be soft deleted twice."""
        doc = Document(company_id=1, name="Test Document")

        doc.soft_delete("user1")

        with self.assertRaisesRegex(ValueError, "Document is already deleted"):
            doc.soft_delete("user2")

    def test_document_should_restore_from_soft_delete(self) -> None:
        """Test that Document can be restored after soft delete."""
        doc = Document(company_id=1, name="Test Document")

        doc.soft_delete("test_user")
        self.assertTrue(doc.is_deleted)

        doc.restore()
        self.assertFalse(doc.is_deleted)
        self.assertIsNone(doc.deleted_at)
        self.assertEqual(doc.deleted_by, "")
        self.assertTrue(doc.is_active())

    def test_document_should_not_restore_if_not_deleted(self) -> None:
        """Test that Document cannot be restored if not deleted."""
        doc = Document(company_id=1, name="Test Document")

        with self.assertRaisesRegex(ValueError, "Document is not deleted"):
            doc.restore()

    def test_document_should_support_signer_management(self) -> None:
        """Test that Document can manage signers."""
        doc = Document(company_id=1, name="Test Document")

        # Initially no signers
        self.assertEqual(len(doc.signer_ids), 0)
        self.assertFalse(doc.can_be_signed())

        # Add signers
        doc.add_signer(100)
        doc.add_signer(200)
        self.assertEqual(len(doc.signer_ids), 2)
        self.assertIn(100, doc.signer_ids)
        self.assertIn(200, doc.signer_ids)
        self.assertTrue(doc.can_be_signed())

        # Don't add duplicate signers
        doc.add_signer(100)
        self.assertEqual(len(doc.signer_ids), 2)

    def test_document_should_include_signers_list_when_loaded_from_repository(self) -> None:
        """Test that Document should have a signers field containing Signer entities."""
        # Create some signer entities
        signer1 = Signer(
            id=1,
            name="João Silva",
            email="joao.silva@example.com",
            token="signer_token_abc123",
            status="pending",
            external_id="ext_signer_001",
            created_at=datetime.now(timezone.utc),
            last_updated_at=datetime.now(timezone.utc)
        )
        signer2 = Signer(
            id=2,
            name="Maria Santos",
            email="maria.santos@example.com",
            token="signer_token_def456",
            status="signed",
            external_id="ext_signer_002",
            created_at=datetime.now(timezone.utc),
            last_updated_at=datetime.now(timezone.utc)
        )

        # Create document with signers list
        doc = Document(
            company_id=1,
            name="Test Document",
            signers=[signer1, signer2],
            signer_ids=[1, 2]  # Keep backward compatibility
        )

        # Document should have signers list
        self.assertEqual(len(doc.signers), 2)
        self.assertIsInstance(doc.signers[0], Signer)
        self.assertIsInstance(doc.signers[1], Signer)
        self.assertEqual(doc.signers[0].name, "João Silva")
        self.assertEqual(doc.signers[1].name, "Maria Santos")

    def test_document_should_default_to_empty_signers_list_when_created(self) -> None:
        """Test that Document defaults to empty signers list."""
        doc = Document(company_id=1, name="Test Document")

        self.assertEqual(len(doc.signers), 0)
        self.assertIsInstance(doc.signers, list)

    def test_document_can_be_signed_should_check_signers_list_not_empty(self) -> None:
        """Test that can_be_signed() checks signers list instead of just signer_ids."""
        doc = Document(company_id=1, name="Test Document")

        # Initially no signers
        self.assertFalse(doc.can_be_signed())

        # Add signer entity to signers list
        signer = Signer(id=1, name="Test Signer", email="test@example.com")
        doc.signers.append(signer)

        # Now it can be signed
        self.assertTrue(doc.can_be_signed())