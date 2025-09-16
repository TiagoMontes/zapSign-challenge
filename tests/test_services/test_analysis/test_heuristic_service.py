import unittest
from datetime import datetime, timezone
from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis
from core.services.analysis.heuristic_service import HeuristicAnalysisService


class TestHeuristicAnalysisService(unittest.TestCase):
    """Test cases for HeuristicAnalysisService."""

    def setUp(self):
        """Set up test dependencies."""
        self.service = HeuristicAnalysisService()

    def test_analyze_contract_document(self):
        """Test analyzing a contract document."""
        document = Document(
            id=1,
            company_id=1,
            name="Service Agreement Contract",
            status="draft",
            created_by="user@example.com"
        )

        analysis = self.service.analyze_document(document)

        self.assertIsInstance(analysis, DocumentAnalysis)
        self.assertEqual(analysis.document_id, 1)
        self.assertIn("Contract document", analysis.summary)
        self.assertIn("Service Agreement Contract", analysis.summary)
        self.assertIsNotNone(analysis.analyzed_at)
        self.assertGreater(len(analysis.missing_topics), 0)
        self.assertGreater(len(analysis.insights), 0)

    def test_analyze_proposal_document(self):
        """Test analyzing a proposal document."""
        document = Document(
            id=2,
            company_id=1,
            name="Project Proposal 2024",
            status="pending",
            created_by="manager@example.com"
        )

        analysis = self.service.analyze_document(document)

        self.assertIsInstance(analysis, DocumentAnalysis)
        self.assertEqual(analysis.document_id, 2)
        self.assertIn("Proposal document", analysis.summary)
        self.assertIn("Project Proposal 2024", analysis.summary)
        self.assertIsNotNone(analysis.analyzed_at)
        self.assertGreater(len(analysis.missing_topics), 0)
        self.assertGreater(len(analysis.insights), 0)

    def test_analyze_legal_document(self):
        """Test analyzing a legal document."""
        document = Document(
            id=3,
            company_id=1,
            name="Terms and Conditions",
            status="",
            created_by="legal@example.com"
        )

        analysis = self.service.analyze_document(document)

        self.assertIsInstance(analysis, DocumentAnalysis)
        self.assertEqual(analysis.document_id, 3)
        self.assertIn("Legal document", analysis.summary)
        self.assertIn("Terms and Conditions", analysis.summary)
        self.assertIsNotNone(analysis.analyzed_at)

    def test_analyze_general_document(self):
        """Test analyzing a general document."""
        document = Document(
            id=4,
            company_id=1,
            name="Meeting Notes",
            status="active",
            created_by="admin@example.com"
        )

        analysis = self.service.analyze_document(document)

        self.assertIsInstance(analysis, DocumentAnalysis)
        self.assertEqual(analysis.document_id, 4)
        self.assertIn("Meeting Notes", analysis.summary)
        self.assertIsNotNone(analysis.analyzed_at)

    def test_validate_document_success(self):
        """Test successful document validation."""
        document = Document(
            id=1,
            company_id=1,
            name="Valid Document",
            status="draft",
            created_by="user@example.com"
        )

        # Should not raise exception
        self.service._validate_document(document)

    def test_validate_document_failure(self):
        """Test document validation failure."""
        # Document without ID (not persisted)
        document = Document(
            company_id=1,
            name="Invalid Document",
            status="draft",
            created_by="user@example.com"
        )

        with self.assertRaises(ValueError) as cm:
            self.service._validate_document(document)
        self.assertIn("cannot be analyzed", str(cm.exception))

    def test_validate_soft_deleted_document(self):
        """Test validation of soft deleted document."""
        document = Document(
            id=1,
            company_id=1,
            name="Deleted Document",
            status="draft",
            created_by="user@example.com"
        )
        document.soft_delete("admin")

        with self.assertRaises(ValueError) as cm:
            self.service._validate_document(document)
        self.assertIn("cannot be analyzed", str(cm.exception))

    def test_classify_document_type(self):
        """Test document type classification."""
        # Contract document
        contract_doc = Document(
            id=1,
            company_id=1,
            name="Service Contract Agreement",
            status="draft",
            created_by="user@example.com"
        )
        content = self.service._extract_content(contract_doc)
        doc_type = self.service._classify_document_type(contract_doc, content)
        self.assertEqual(doc_type, "contract")

        # Proposal document
        proposal_doc = Document(
            id=2,
            company_id=1,
            name="Project Proposal",
            status="draft",
            created_by="user@example.com"
        )
        content = self.service._extract_content(proposal_doc)
        doc_type = self.service._classify_document_type(proposal_doc, content)
        self.assertEqual(doc_type, "proposal")

        # Legal document
        legal_doc = Document(
            id=3,
            company_id=1,
            name="Privacy Policy",
            status="draft",
            created_by="user@example.com"
        )
        content = self.service._extract_content(legal_doc)
        doc_type = self.service._classify_document_type(legal_doc, content)
        self.assertEqual(doc_type, "legal")

        # General document
        general_doc = Document(
            id=4,
            company_id=1,
            name="Meeting Notes",
            status="draft",
            created_by="user@example.com"
        )
        content = self.service._extract_content(general_doc)
        doc_type = self.service._classify_document_type(general_doc, content)
        self.assertEqual(doc_type, "general")

    def test_insights_based_on_status(self):
        """Test that insights vary based on document status."""
        # Draft document
        draft_doc = Document(
            id=1,
            company_id=1,
            name="Draft Contract",
            status="draft",
            created_by="user@example.com"
        )
        content = self.service._extract_content(draft_doc)
        insights = self.service._generate_insights(draft_doc, "contract", content)
        self.assertTrue(any("draft status" in insight.lower() for insight in insights))

        # Pending document
        pending_doc = Document(
            id=2,
            company_id=1,
            name="Pending Contract",
            status="pending",
            created_by="user@example.com"
        )
        content = self.service._extract_content(pending_doc)
        insights = self.service._generate_insights(pending_doc, "contract", content)
        self.assertTrue(any("pending" in insight.lower() for insight in insights))

    def test_analysis_completeness(self):
        """Test that analysis results are complete."""
        document = Document(
            id=1,
            company_id=1,
            name="Test Document",
            status="draft",
            created_by="user@example.com"
        )

        analysis = self.service.analyze_document(document)

        # Check all required fields are populated
        self.assertEqual(analysis.document_id, 1)
        self.assertNotEqual(analysis.summary.strip(), "")
        self.assertIsNotNone(analysis.analyzed_at)
        self.assertIsInstance(analysis.analyzed_at, datetime)
        self.assertIsNotNone(analysis.analyzed_at.tzinfo)  # Should have timezone info

        # Check that analysis is meaningful
        self.assertTrue(analysis.has_meaningful_analysis())

        # Check that analysis is complete
        self.assertTrue(analysis.is_complete())