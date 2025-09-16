"""Integration tests for DocumentViewSet to ensure use case delegation."""

import json
from typing import cast
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse
from rest_framework.test import APIClient
from rest_framework import status
from core.orm.models import Document as DocumentModel, Company as CompanyModel


class TestDocumentViewSetIntegration(TestCase):
    """Integration tests for DocumentViewSet."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test company
        self.company = CompanyModel.objects.create(
            name="Test Company",
            api_token="test-token"
        )

        # Create test documents
        self.doc1 = DocumentModel.objects.create(
            company=self.company,
            name="Document 1",
            status="draft",
            token="doc1-token",
            created_by="test_user",
            external_id="ext_1"
        )

        self.doc2 = DocumentModel.objects.create(
            company=self.company,
            name="Document 2",
            status="pending",
            token="doc2-token",
            created_by="test_user",
            external_id="ext_2"
        )

    def test_document_list_should_return_standardized_response_format(self):
        """Test that document list returns standardized response format."""
        url = reverse('document-list')
        response = cast(HttpResponse, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should return standardized response format
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('success', data)
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Should be successful
        self.assertTrue(data['success'])
        self.assertEqual(data['code'], status.HTTP_200_OK)

        # Data should contain documents
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 2)

    def test_document_retrieve_should_return_standardized_response_format(self):
        """Test that document retrieve returns standardized response format."""
        url = reverse('document-detail', kwargs={'pk': self.doc1.id})
        response = cast(HttpResponse, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should return standardized response format
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('success', data)
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Should be successful
        self.assertTrue(data['success'])
        self.assertEqual(data['code'], status.HTTP_200_OK)

        # Data should contain the document
        self.assertIsInstance(data['data'], dict)
        self.assertEqual(data['data']['id'], self.doc1.id)
        self.assertEqual(data['data']['name'], "Document 1")

    def test_document_retrieve_should_return_404_for_nonexistent_document(self):
        """Test that document retrieve returns 404 for nonexistent document."""
        url = reverse('document-detail', kwargs={'pk': 99999})
        response = cast(HttpResponse, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should return standardized error response format
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('success', data)
        self.assertIn('code', data)
        self.assertIn('message', data)

        # Should indicate failure
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], status.HTTP_404_NOT_FOUND)

    def test_document_update_should_return_method_not_allowed(self):
        """Test that document update returns method not allowed."""
        url = reverse('document-detail', kwargs={'pk': self.doc1.id})
        response = cast(HttpResponse, self.client.put(url, data={'name': 'Updated Name'}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Should return standardized error response format
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('success', data)
        self.assertIn('code', data)
        self.assertIn('message', data)

        # Should indicate failure
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_document_partial_update_should_return_method_not_allowed(self):
        """Test that document partial update returns method not allowed."""
        url = reverse('document-detail', kwargs={'pk': self.doc1.id})
        response = cast(HttpResponse, self.client.patch(url, data={'name': 'Updated Name'}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Should return standardized error response format
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('success', data)
        self.assertIn('code', data)
        self.assertIn('message', data)

        # Should indicate failure
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], status.HTTP_405_METHOD_NOT_ALLOWED)