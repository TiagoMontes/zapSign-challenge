import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis
from core.use_cases.analyze_document import AnalyzeDocumentUseCase, GetDocumentAnalysisUseCase
from core.services.analysis.interfaces import AnalysisError


class TestAnalyzeDocumentUseCase(unittest.TestCase):
    """Test cases for AnalyzeDocumentUseCase."""

    def setUp(self):
        """Set up test dependencies."""
        self.document_repository = Mock()
        self.analysis_repository = Mock()
        self.analysis_service = Mock()

        self.use_case = AnalyzeDocumentUseCase(
            document_repository=self.document_repository,
            analysis_repository=self.analysis_repository,
            analysis_service=self.analysis_service
        )

    def test_execute_success(self):
        """Test successful document analysis."""
        # Arrange
        document_id = 1
        document = Document(
            id=document_id,
            company_id=1,
            name="Test Contract",
            status="draft",
            created_by="user@example.com",
            processing_status="INDEXED"  # Required for analysis
        )

        analysis = DocumentAnalysis(
            document_id=document_id,
            summary="Test analysis summary",
            missing_topics=["Payment terms"],
            insights=["Review contract carefully"],
            analyzed_at=datetime.now(timezone.utc)
        )

        saved_analysis = DocumentAnalysis(
            id=1,
            document_id=document_id,
            summary="Test analysis summary",
            missing_topics=["Payment terms"],
            insights=["Review contract carefully"],
            analyzed_at=datetime.now(timezone.utc)
        )

        # Mock repository responses
        self.document_repository.find_by_id.return_value = document
        self.analysis_repository.get_by_document_id.return_value = None  # No existing analysis
        self.analysis_service.analyze_document.return_value = analysis
        self.analysis_repository.save.return_value = saved_analysis

        # Act
        result = self.use_case.execute(document_id)

        # Assert
        self.assertEqual(result, saved_analysis)
        self.document_repository.find_by_id.assert_called_once_with(document_id)
        self.analysis_repository.get_by_document_id.assert_called_once_with(document_id)
        self.analysis_service.analyze_document.assert_called_once_with(document)
        self.analysis_repository.save.assert_called_once()

        # Verify the analysis was prepared correctly
        saved_analysis_call = self.analysis_repository.save.call_args[0][0]
        self.assertEqual(saved_analysis_call.document_id, document_id)

    def test_execute_document_not_found(self):
        """Test execution when document is not found."""
        # Arrange
        document_id = 999
        self.document_repository.find_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.use_case.execute(document_id)
        self.assertIn("Document with id 999 not found", str(cm.exception))

        self.document_repository.find_by_id.assert_called_once_with(document_id)
        self.analysis_service.analyze_document.assert_not_called()

    def test_execute_document_cannot_be_analyzed(self):
        """Test execution when document cannot be analyzed."""
        # Arrange
        document_id = 1
        document = Document(
            company_id=1,  # No ID - not persisted
            name="Test Contract",
            status="draft",
            created_by="user@example.com"
        )

        self.document_repository.find_by_id.return_value = document

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.use_case.execute(document_id)
        self.assertIn("cannot be analyzed", str(cm.exception))

        self.document_repository.find_by_id.assert_called_once_with(document_id)
        self.analysis_service.analyze_document.assert_not_called()

    def test_execute_existing_analysis_found(self):
        """Test execution when analysis already exists."""
        # Arrange
        document_id = 1
        document = Document(
            id=document_id,
            company_id=1,
            name="Test Contract",
            status="draft",
            created_by="user@example.com",
            processing_status="INDEXED"  # Required for analysis
        )

        existing_analysis = DocumentAnalysis(
            id=1,
            document_id=document_id,
            summary="Existing analysis",
            analyzed_at=datetime.now(timezone.utc)
        )

        self.document_repository.find_by_id.return_value = document
        self.analysis_repository.get_by_document_id.return_value = existing_analysis

        # Act
        result = self.use_case.execute(document_id)

        # Assert
        self.assertEqual(result, existing_analysis)
        self.document_repository.find_by_id.assert_called_once_with(document_id)
        self.analysis_repository.get_by_document_id.assert_called_once_with(document_id)
        self.analysis_service.analyze_document.assert_not_called()  # Should not analyze again

    def test_execute_analysis_service_error(self):
        """Test execution when analysis service fails."""
        # Arrange
        document_id = 1
        document = Document(
            id=document_id,
            company_id=1,
            name="Test Contract",
            status="draft",
            created_by="user@example.com",
            processing_status="INDEXED"  # Required for analysis
        )

        self.document_repository.find_by_id.return_value = document
        self.analysis_repository.get_by_document_id.return_value = None
        self.analysis_service.analyze_document.side_effect = AnalysisError("AI service failed")

        # Act & Assert
        with self.assertRaises(AnalysisError) as cm:
            self.use_case.execute(document_id)
        self.assertIn("AI service failed", str(cm.exception))

    def test_execute_no_meaningful_analysis(self):
        """Test execution when analysis produces no meaningful results."""
        # Arrange
        document_id = 1
        document = Document(
            id=document_id,
            company_id=1,
            name="Test Contract",
            status="draft",
            created_by="user@example.com",
            processing_status="INDEXED"  # Required for analysis
        )

        # Analysis with no meaningful content
        analysis = DocumentAnalysis(
            document_id=document_id,
            summary="",
            missing_topics=[],
            insights=[],
            analyzed_at=datetime.now(timezone.utc)
        )

        self.document_repository.find_by_id.return_value = document
        self.analysis_repository.get_by_document_id.return_value = None
        self.analysis_service.analyze_document.return_value = analysis

        # Act & Assert
        with self.assertRaises(AnalysisError) as cm:
            self.use_case.execute(document_id)
        self.assertIn("Analysis produced no meaningful results", str(cm.exception))

    def test_execute_unexpected_error(self):
        """Test execution with unexpected error."""
        # Arrange
        document_id = 1
        document = Document(
            id=document_id,
            company_id=1,
            name="Test Contract",
            status="draft",
            created_by="user@example.com",
            processing_status="INDEXED"  # Required for analysis
        )

        self.document_repository.find_by_id.return_value = document
        self.analysis_repository.get_by_document_id.return_value = None
        self.analysis_service.analyze_document.side_effect = Exception("Unexpected error")

        # Act & Assert
        with self.assertRaises(AnalysisError) as cm:
            self.use_case.execute(document_id)
        self.assertIn("Analysis failed: Unexpected error", str(cm.exception))


class TestGetDocumentAnalysisUseCase(unittest.TestCase):
    """Test cases for GetDocumentAnalysisUseCase."""

    def setUp(self):
        """Set up test dependencies."""
        self.analysis_repository = Mock()
        self.use_case = GetDocumentAnalysisUseCase(self.analysis_repository)

    def test_execute_success(self):
        """Test successful retrieval of document analysis."""
        # Arrange
        document_id = 1
        analysis = DocumentAnalysis(
            id=1,
            document_id=document_id,
            summary="Test analysis",
            analyzed_at=datetime.now(timezone.utc)
        )

        self.analysis_repository.get_by_document_id.return_value = analysis

        # Act
        result = self.use_case.execute(document_id)

        # Assert
        self.assertEqual(result, analysis)
        self.analysis_repository.get_by_document_id.assert_called_once_with(document_id)

    def test_execute_not_found(self):
        """Test retrieval when analysis not found."""
        # Arrange
        document_id = 999
        self.analysis_repository.get_by_document_id.return_value = None

        # Act
        result = self.use_case.execute(document_id)

        # Assert
        self.assertIsNone(result)
        self.analysis_repository.get_by_document_id.assert_called_once_with(document_id)

    def test_get_by_id_success(self):
        """Test successful retrieval by analysis ID."""
        # Arrange
        analysis_id = 1
        analysis = DocumentAnalysis(
            id=analysis_id,
            document_id=1,
            summary="Test analysis",
            analyzed_at=datetime.now(timezone.utc)
        )

        self.analysis_repository.get_by_id.return_value = analysis

        # Act
        result = self.use_case.get_by_id(analysis_id)

        # Assert
        self.assertEqual(result, analysis)
        self.analysis_repository.get_by_id.assert_called_once_with(analysis_id)

    def test_get_by_id_not_found(self):
        """Test retrieval by ID when analysis not found."""
        # Arrange
        analysis_id = 999
        self.analysis_repository.get_by_id.return_value = None

        # Act
        result = self.use_case.get_by_id(analysis_id)

        # Assert
        self.assertIsNone(result)
        self.analysis_repository.get_by_id.assert_called_once_with(analysis_id)

    def test_list_for_document(self):
        """Test listing all analyses for a document."""
        # Arrange
        document_id = 1
        analyses = [
            DocumentAnalysis(
                id=1,
                document_id=document_id,
                summary="First analysis",
                analyzed_at=datetime.now(timezone.utc)
            ),
            DocumentAnalysis(
                id=2,
                document_id=document_id,
                summary="Second analysis",
                analyzed_at=datetime.now(timezone.utc)
            )
        ]

        self.analysis_repository.list_by_document_id.return_value = analyses

        # Act
        result = self.use_case.list_for_document(document_id)

        # Assert
        self.assertEqual(result, analyses)
        self.analysis_repository.list_by_document_id.assert_called_once_with(document_id)