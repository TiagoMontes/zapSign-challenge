"""Integration tests for SignerViewSet with document_ids field."""

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from core.orm.models import Company, Document, Signer
import json


class SignerViewSetIntegrationTest(TestCase):
    """Test SignerViewSet integration with document_ids field."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()

        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            api_token="test_api_token"
        )

        # Create a signer
        self.signer = Signer.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            token="signer_token_123",
            status="pending",
            external_id="ext_signer_001"
        )

        # Create documents
        self.document1 = Document.objects.create(
            company=self.company,
            name="Document 1",
            status="draft",
            token="doc_token_1",
            external_id="ext_doc_001"
        )

        self.document2 = Document.objects.create(
            company=self.company,
            name="Document 2",
            status="draft",
            token="doc_token_2",
            external_id="ext_doc_002"
        )

        # Associate signer with documents
        self.document1.signers.add(self.signer)
        self.document2.signers.add(self.signer)

    def test_retrieve_signer_should_include_document_ids(self) -> None:
        """Test that retrieving a signer includes document_ids in response."""
        url = reverse('signer-detail', kwargs={'pk': self.signer.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)

        # Check response structure
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('code'), 200)
        self.assertEqual(response_data.get('message'), "Signer retrieved successfully")

        # Check signer data
        signer_data = response_data.get('data')
        self.assertIsNotNone(signer_data)

        # Check basic signer fields
        self.assertEqual(signer_data.get('id'), self.signer.id)
        self.assertEqual(signer_data.get('name'), "John Doe")
        self.assertEqual(signer_data.get('email'), "john.doe@example.com")
        self.assertEqual(signer_data.get('token'), "signer_token_123")
        self.assertEqual(signer_data.get('status'), "pending")
        self.assertEqual(signer_data.get('external_id'), "ext_signer_001")

        # Check document_ids field
        document_ids = signer_data.get('document_ids')
        self.assertIsNotNone(document_ids)
        self.assertIsInstance(document_ids, list)
        self.assertEqual(len(document_ids), 2)
        self.assertIn(self.document1.id, document_ids)
        self.assertIn(self.document2.id, document_ids)

    def test_list_signers_should_include_document_ids(self) -> None:
        """Test that listing signers includes document_ids for each signer."""
        url = reverse('signer-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)

        # Check response structure
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('code'), 200)
        self.assertEqual(response_data.get('message'), "Signers retrieved successfully")

        # Check signers data
        signers_data = response_data.get('data')
        self.assertIsNotNone(signers_data)
        self.assertIsInstance(signers_data, list)
        self.assertGreaterEqual(len(signers_data), 1)

        # Find our signer in the list
        our_signer = None
        for signer in signers_data:
            if signer.get('id') == self.signer.id:
                our_signer = signer
                break

        self.assertIsNotNone(our_signer)

        # Check document_ids field
        document_ids = our_signer.get('document_ids')
        self.assertIsNotNone(document_ids)
        self.assertIsInstance(document_ids, list)
        self.assertEqual(len(document_ids), 2)
        self.assertIn(self.document1.id, document_ids)
        self.assertIn(self.document2.id, document_ids)

    def test_signer_with_no_documents_should_have_empty_document_ids(self) -> None:
        """Test that a signer with no documents has empty document_ids list."""
        # Create a signer without documents
        standalone_signer = Signer.objects.create(
            name="Jane Doe",
            email="jane.doe@example.com",
            token="signer_token_456",
            status="new",
            external_id="ext_signer_002"
        )

        url = reverse('signer-detail', kwargs={'pk': standalone_signer.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        signer_data = response_data.get('data')

        # Check document_ids field is empty list
        document_ids = signer_data.get('document_ids')
        self.assertIsNotNone(document_ids)
        self.assertIsInstance(document_ids, list)
        self.assertEqual(len(document_ids), 0)