import json
from django.test import TestCase, Client
from django.urls import reverse
from core.orm.models import Company, Document


class DocumentAnalysisAPITest(TestCase):
    """Test the document analysis API endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            api_token="test_token"
        )

        # Create a document
        self.document = Document.objects.create(
            company=self.company,
            name="Test Contract Agreement",
            status="draft",
            created_by="test_user@example.com"
        )

    def test_analyze_document_success(self):
        """Test successful document analysis via API."""
        url = f"/api/documents/{self.document.id}/analyze/"

        response = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("data", response_data)

        # Check analysis data structure
        analysis_data = response_data["data"]
        self.assertIn("analysis", analysis_data)

        analysis = analysis_data["analysis"]
        self.assertEqual(analysis["document_id"], self.document.id)
        self.assertIsNotNone(analysis["summary"])
        self.assertIsInstance(analysis["missing_topics"], list)
        self.assertIsInstance(analysis["insights"], list)
        self.assertIsNotNone(analysis["analyzed_at"])

    def test_analyze_nonexistent_document(self):
        """Test analysis of non-existent document."""
        url = "/api/documents/99999/analyze/"

        response = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("not found", response_data["message"])

    def test_analyze_invalid_document_id(self):
        """Test analysis with invalid document ID."""
        url = "/api/documents/invalid/analyze/"

        response = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("Invalid document ID", response_data["message"])

    def test_analyze_soft_deleted_document(self):
        """Test analysis of soft deleted document."""
        # Soft delete the document
        from core.orm.mappers import DocumentMapper
        document_entity = DocumentMapper.to_entity(self.document)
        document_entity.soft_delete("admin")

        # Save the changes back to the model
        model_data = DocumentMapper.to_model_data(document_entity)
        for key, value in model_data.items():
            setattr(self.document, key, value)
        self.document.save()

        url = f"/api/documents/{self.document.id}/analyze/"

        response = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("cannot be analyzed", response_data["message"])

    def test_duplicate_analysis_handling(self):
        """Test handling of duplicate analysis requests."""
        url = f"/api/documents/{self.document.id}/analyze/"

        # First analysis
        response1 = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 200)

        # Second analysis - should return existing
        response2 = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 200)

        # Both should have the same analysis ID
        analysis1 = response1.json()["data"]["analysis"]
        analysis2 = response2.json()["data"]["analysis"]
        self.assertEqual(analysis1["id"], analysis2["id"])


if __name__ == '__main__':
    import unittest
    unittest.main()