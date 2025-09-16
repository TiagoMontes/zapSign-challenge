"""Tests for Document entity."""

import unittest
from datetime import datetime, timezone
from core.domain.entities.document import Document


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