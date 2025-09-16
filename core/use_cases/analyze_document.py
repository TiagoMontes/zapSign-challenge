from typing import Optional

from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis
from core.repositories.contracts import DocumentRepository as DocumentRepositoryProtocol
from core.repositories.document_analysis_repository import DocumentAnalysisRepositoryProtocol
from core.services.analysis.interfaces import AnalysisService, AnalysisError


class AnalyzeDocumentUseCase:
    """Use case for analyzing documents with AI/heuristic services.

    This use case orchestrates the document analysis process:
    1. Validates document can be analyzed
    2. Retrieves document from repository
    3. Performs analysis using configured service
    4. Persists analysis results
    """

    def __init__(
        self,
        document_repository: DocumentRepositoryProtocol,
        analysis_repository: DocumentAnalysisRepositoryProtocol,
        analysis_service: AnalysisService,
    ):
        """Initialize the use case with dependencies.

        Args:
            document_repository: Repository for document operations
            analysis_repository: Repository for analysis operations
            analysis_service: Service for performing analysis
        """
        self.document_repository = document_repository
        self.analysis_repository = analysis_repository
        self.analysis_service = analysis_service

    def execute(self, document_id: int, force_reanalyze: bool = False) -> DocumentAnalysis:
        """Execute document analysis.

        Args:
            document_id: ID of the document to analyze
            force_reanalyze: If True, forces a new analysis even if one exists

        Returns:
            DocumentAnalysis: The analysis results

        Raises:
            ValueError: If document not found or cannot be analyzed
            AnalysisError: If analysis fails
        """
        # Retrieve document
        document = self.document_repository.find_by_id(document_id)
        if not document:
            raise ValueError(f"Document with id {document_id} not found")

        # Validate document can be analyzed
        if not document.can_be_analyzed():
            raise ValueError(
                f"Document {document_id} cannot be analyzed. "
                f"Check if document is active and has content."
            )

        # Check if analysis already exists
        existing_analysis = self.analysis_repository.get_by_document_id(document_id)
        if existing_analysis and not force_reanalyze:
            # Return existing analysis unless forced to reanalyze
            return existing_analysis

        try:
            # Perform analysis
            analysis = self.analysis_service.analyze_document(document)

            # Ensure document_id is set
            analysis.document_id = document_id

            # Validate analysis
            if not analysis.has_meaningful_analysis():
                raise AnalysisError("Analysis produced no meaningful results")

            # If forcing reanalysis and existing analysis exists, delete it first
            if force_reanalyze and existing_analysis and existing_analysis.id:
                self.analysis_repository.delete(existing_analysis.id)

            # Save analysis
            saved_analysis = self.analysis_repository.save(analysis)

            return saved_analysis

        except AnalysisError:
            # Re-raise analysis errors
            raise
        except Exception as e:
            # Wrap other exceptions as analysis errors
            raise AnalysisError(f"Analysis failed: {str(e)}", e)


class GetDocumentAnalysisUseCase:
    """Use case for retrieving existing document analysis."""

    def __init__(
        self,
        analysis_repository: DocumentAnalysisRepositoryProtocol,
    ):
        """Initialize the use case.

        Args:
            analysis_repository: Repository for analysis operations
        """
        self.analysis_repository = analysis_repository

    def execute(self, document_id: int) -> Optional[DocumentAnalysis]:
        """Get the latest analysis for a document.

        Args:
            document_id: ID of the document

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        return self.analysis_repository.get_by_document_id(document_id)

    def get_by_id(self, analysis_id: int) -> Optional[DocumentAnalysis]:
        """Get analysis by its ID.

        Args:
            analysis_id: ID of the analysis

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        return self.analysis_repository.get_by_id(analysis_id)

    def list_for_document(self, document_id: int) -> list[DocumentAnalysis]:
        """List all analyses for a document.

        Args:
            document_id: ID of the document

        Returns:
            List of DocumentAnalysis entities
        """
        return self.analysis_repository.list_by_document_id(document_id)