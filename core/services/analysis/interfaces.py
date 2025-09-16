from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis


@runtime_checkable
class AnalysisService(Protocol):
    """Protocol for document analysis services.

    This defines the interface that all analysis services must implement,
    following the strategy pattern for pluggable analysis backends.
    """

    def analyze_document(self, document: Document) -> DocumentAnalysis:
        """Analyze a document and return analysis results.

        Args:
            document: The document entity to analyze

        Returns:
            DocumentAnalysis: The analysis results

        Raises:
            AnalysisError: If analysis fails
        """
        ...


class BaseAnalysisService(ABC):
    """Abstract base class for analysis services.

    Provides common functionality and enforces the interface contract.
    """

    @abstractmethod
    def analyze_document(self, document: Document) -> DocumentAnalysis:
        """Analyze a document and return analysis results.

        Args:
            document: The document entity to analyze

        Returns:
            DocumentAnalysis: The analysis results

        Raises:
            AnalysisError: If analysis fails
        """
        pass

    def _validate_document(self, document: Document) -> None:
        """Validate that document can be analyzed.

        Args:
            document: The document to validate

        Raises:
            ValueError: If document cannot be analyzed
        """
        if not document.can_be_analyzed():
            raise ValueError(
                f"Document {document.id} cannot be analyzed. "
                f"Check if document is active and has content."
            )


class AnalysisError(Exception):
    """Raised when document analysis fails."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error