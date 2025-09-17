"""Tests for Signer entity."""

import unittest
from datetime import datetime, timezone
from core.domain.entities.signer import Signer


class TestSigner(unittest.TestCase):
    """Test cases for Signer entity."""

    def test_signer_should_be_created_with_basic_fields(self) -> None:
        """Test that Signer can be created with basic fields."""
        signer = Signer(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            token="abc123",
            status="pending",
            external_id="ext_001"
        )

        self.assertEqual(signer.id, 1)
        self.assertEqual(signer.name, "John Doe")
        self.assertEqual(signer.email, "john.doe@example.com")
        self.assertEqual(signer.token, "abc123")
        self.assertEqual(signer.status, "pending")
        self.assertEqual(signer.external_id, "ext_001")

    def test_signer_should_include_document_ids_field(self) -> None:
        """Test that Signer entity includes document_ids field for related documents."""
        # This test will fail initially - following TDD RED phase
        signer = Signer(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            document_ids=[10, 15, 20]
        )

        self.assertEqual(signer.document_ids, [10, 15, 20])
        self.assertIsInstance(signer.document_ids, list)

    def test_signer_should_default_to_empty_document_ids_when_created(self) -> None:
        """Test that Signer defaults to empty document_ids list when not provided."""
        signer = Signer(
            id=1,
            name="John Doe",
            email="john.doe@example.com"
        )

        self.assertEqual(signer.document_ids, [])
        self.assertIsInstance(signer.document_ids, list)

    def test_signer_should_allow_updating_document_ids(self) -> None:
        """Test that Signer allows modifying document_ids after creation."""
        signer = Signer(
            id=1,
            name="John Doe",
            email="john.doe@example.com"
        )

        # Initially empty
        self.assertEqual(signer.document_ids, [])

        # Update document_ids
        signer.document_ids = [5, 10]
        self.assertEqual(signer.document_ids, [5, 10])