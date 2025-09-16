import unittest
from datetime import datetime, timezone
from core.domain.entities.document_analysis import DocumentAnalysis


class TestDocumentAnalysis(unittest.TestCase):
    """Test cases for DocumentAnalysis entity."""

    def test_create_minimal_analysis(self):
        """Test creating a minimal DocumentAnalysis."""
        analysis = DocumentAnalysis(document_id=1)

        self.assertEqual(analysis.document_id, 1)
        self.assertEqual(analysis.missing_topics, [])
        self.assertEqual(analysis.insights, [])
        self.assertEqual(analysis.summary, "")
        self.assertIsNone(analysis.analyzed_at)
        self.assertIsNone(analysis.id)

    def test_create_complete_analysis(self):
        """Test creating a complete DocumentAnalysis."""
        analyzed_at = datetime.now(timezone.utc)
        analysis = DocumentAnalysis(
            id=1,
            document_id=2,
            missing_topics=["Payment terms", "Liability clauses"],
            summary="Contract analysis summary",
            insights=["Review payment terms", "Add liability protection"],
            analyzed_at=analyzed_at
        )

        self.assertEqual(analysis.id, 1)
        self.assertEqual(analysis.document_id, 2)
        self.assertEqual(analysis.missing_topics, ["Payment terms", "Liability clauses"])
        self.assertEqual(analysis.summary, "Contract analysis summary")
        self.assertEqual(analysis.insights, ["Review payment terms", "Add liability protection"])
        self.assertEqual(analysis.analyzed_at, analyzed_at)

    def test_requires_document_id(self):
        """Test that document_id is required."""
        with self.assertRaises(ValueError) as cm:
            DocumentAnalysis()
        self.assertIn("DocumentAnalysis.document_id is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            DocumentAnalysis(document_id=0)
        self.assertIn("DocumentAnalysis.document_id is required", str(cm.exception))

    def test_add_missing_topic(self):
        """Test adding missing topics."""
        analysis = DocumentAnalysis(document_id=1)

        analysis.add_missing_topic("Payment terms")
        self.assertEqual(analysis.missing_topics, ["Payment terms"])

        analysis.add_missing_topic("Liability clauses")
        self.assertEqual(analysis.missing_topics, ["Payment terms", "Liability clauses"])

        # Should not add duplicates
        analysis.add_missing_topic("Payment terms")
        self.assertEqual(analysis.missing_topics, ["Payment terms", "Liability clauses"])

        # Should not add empty or whitespace-only topics
        analysis.add_missing_topic("")
        analysis.add_missing_topic("   ")
        self.assertEqual(analysis.missing_topics, ["Payment terms", "Liability clauses"])

    def test_add_insight(self):
        """Test adding insights."""
        analysis = DocumentAnalysis(document_id=1)

        analysis.add_insight("Review payment terms")
        self.assertEqual(analysis.insights, ["Review payment terms"])

        analysis.add_insight("Add liability protection")
        self.assertEqual(analysis.insights, ["Review payment terms", "Add liability protection"])

        # Should not add duplicates
        analysis.add_insight("Review payment terms")
        self.assertEqual(analysis.insights, ["Review payment terms", "Add liability protection"])

        # Should not add empty or whitespace-only insights
        analysis.add_insight("")
        analysis.add_insight("   ")
        self.assertEqual(analysis.insights, ["Review payment terms", "Add liability protection"])

    def test_has_meaningful_analysis(self):
        """Test has_meaningful_analysis method."""
        # Empty analysis
        analysis = DocumentAnalysis(document_id=1)
        self.assertFalse(analysis.has_meaningful_analysis())

        # With summary only
        analysis = DocumentAnalysis(document_id=1, summary="Contract summary")
        self.assertTrue(analysis.has_meaningful_analysis())

        # With missing topics only
        analysis = DocumentAnalysis(document_id=1, missing_topics=["Payment terms"])
        self.assertTrue(analysis.has_meaningful_analysis())

        # With insights only
        analysis = DocumentAnalysis(document_id=1, insights=["Review contract"])
        self.assertTrue(analysis.has_meaningful_analysis())

        # With whitespace-only summary
        analysis = DocumentAnalysis(document_id=1, summary="   ")
        self.assertFalse(analysis.has_meaningful_analysis())

    def test_is_complete(self):
        """Test is_complete method."""
        # Incomplete analysis
        analysis = DocumentAnalysis(document_id=1)
        self.assertFalse(analysis.is_complete())

        # Missing analyzed_at
        analysis = DocumentAnalysis(
            document_id=1,
            summary="Contract summary"
        )
        self.assertFalse(analysis.is_complete())

        # Missing summary
        analysis = DocumentAnalysis(
            document_id=1,
            analyzed_at=datetime.now(timezone.utc)
        )
        self.assertFalse(analysis.is_complete())

        # Complete analysis
        analysis = DocumentAnalysis(
            document_id=1,
            summary="Contract summary",
            analyzed_at=datetime.now(timezone.utc)
        )
        self.assertTrue(analysis.is_complete())

    def test_whitespace_handling(self):
        """Test proper handling of whitespace in topics and insights."""
        analysis = DocumentAnalysis(document_id=1)

        # Test whitespace trimming
        analysis.add_missing_topic("  Payment terms  ")
        self.assertEqual(analysis.missing_topics, ["Payment terms"])

        analysis.add_insight("  Review contract  ")
        self.assertEqual(analysis.insights, ["Review contract"])


if __name__ == '__main__':
    unittest.main()