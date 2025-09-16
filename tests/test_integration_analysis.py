import unittest
from django.test import TestCase
from core.orm.models import Company, Document, DocumentAnalysis
from core.repositories.document_repo import DjangoDocumentRepository
from core.repositories.document_analysis_repository import DocumentAnalysisRepository
from core.services.analysis.heuristic_service import HeuristicAnalysisService
from core.use_cases.analyze_document import AnalyzeDocumentUseCase


class DocumentAnalysisIntegrationTest(TestCase):
    """Integration test for document analysis feature."""

    def setUp(self):
        """Set up test data."""
        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            api_token="test_token"
        )

        # Create a document
        self.document_model = Document.objects.create(
            company=self.company,
            name="Test Contract Agreement",
            status="draft",
            created_by="test_user@example.com"
        )

    def test_complete_analysis_workflow(self):
        """Test the complete document analysis workflow."""
        # Arrange
        document_repository = DjangoDocumentRepository()
        analysis_repository = DocumentAnalysisRepository()
        analysis_service = HeuristicAnalysisService()

        use_case = AnalyzeDocumentUseCase(
            document_repository=document_repository,
            analysis_repository=analysis_repository,
            analysis_service=analysis_service
        )

        # Act
        analysis = use_case.execute(self.document_model.id)

        # Assert
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.document_id, self.document_model.id)
        self.assertIsNotNone(analysis.id)  # Should be saved with ID
        self.assertTrue(analysis.has_meaningful_analysis())
        self.assertTrue(analysis.is_complete())

        # Verify it was saved to database
        saved_analysis = DocumentAnalysis.objects.filter(
            document_id=self.document_model.id
        ).first()
        self.assertIsNotNone(saved_analysis)
        self.assertEqual(saved_analysis.id, analysis.id)

    def test_document_analysis_orm_mapping(self):
        """Test ORM model to entity mapping."""
        from core.orm.mappers import DocumentAnalysisMapper
        from datetime import datetime, timezone

        # Create analysis via ORM
        analysis_model = DocumentAnalysis.objects.create(
            document=self.document_model,
            summary="Test analysis summary",
            missing_topics=["Payment terms", "Liability"],
            insights=["Review carefully", "Add clauses"],
        )

        # Convert to entity
        analysis_entity = DocumentAnalysisMapper.to_entity(analysis_model)

        # Verify mapping
        self.assertEqual(analysis_entity.id, analysis_model.id)
        self.assertEqual(analysis_entity.document_id, self.document_model.id)
        self.assertEqual(analysis_entity.summary, "Test analysis summary")
        self.assertEqual(analysis_entity.missing_topics, ["Payment terms", "Liability"])
        self.assertEqual(analysis_entity.insights, ["Review carefully", "Add clauses"])
        self.assertIsNotNone(analysis_entity.analyzed_at)

    def test_repository_operations(self):
        """Test document analysis repository operations."""
        from core.domain.entities.document_analysis import DocumentAnalysis as AnalysisEntity
        from datetime import datetime, timezone

        repository = DocumentAnalysisRepository()

        # Create and save analysis
        analysis = AnalysisEntity(
            document_id=self.document_model.id,
            summary="Repository test analysis",
            missing_topics=["Topic 1", "Topic 2"],
            insights=["Insight 1", "Insight 2"],
            analyzed_at=datetime.now(timezone.utc)
        )

        saved_analysis = repository.save(analysis)

        # Verify save worked
        self.assertIsNotNone(saved_analysis.id)
        self.assertEqual(saved_analysis.document_id, self.document_model.id)

        # Test get by ID
        retrieved_analysis = repository.get_by_id(saved_analysis.id)
        self.assertIsNotNone(retrieved_analysis)
        self.assertEqual(retrieved_analysis.id, saved_analysis.id)

        # Test get by document ID
        doc_analysis = repository.get_by_document_id(self.document_model.id)
        self.assertIsNotNone(doc_analysis)
        self.assertEqual(doc_analysis.id, saved_analysis.id)

        # Test list by document ID
        analyses = repository.list_by_document_id(self.document_model.id)
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0].id, saved_analysis.id)

    def test_document_can_be_analyzed_rule(self):
        """Test document business rule for analysis eligibility."""
        from core.orm.mappers import DocumentMapper

        # Convert to entity
        document_entity = DocumentMapper.to_entity(self.document_model)

        # Should be analyzable
        self.assertTrue(document_entity.can_be_analyzed())

        # Test soft deleted document
        document_entity.soft_delete("test_user")
        self.assertFalse(document_entity.can_be_analyzed())

    def test_duplicate_analysis_prevention(self):
        """Test that duplicate analysis is prevented."""
        document_repository = DjangoDocumentRepository()
        analysis_repository = DocumentAnalysisRepository()
        analysis_service = HeuristicAnalysisService()

        use_case = AnalyzeDocumentUseCase(
            document_repository=document_repository,
            analysis_repository=analysis_repository,
            analysis_service=analysis_service
        )

        # First analysis
        analysis1 = use_case.execute(self.document_model.id)

        # Second analysis attempt
        analysis2 = use_case.execute(self.document_model.id)

        # Should return the same analysis (existing one)
        self.assertEqual(analysis1.id, analysis2.id)

        # Verify only one analysis exists in database
        count = DocumentAnalysis.objects.filter(
            document_id=self.document_model.id
        ).count()
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()