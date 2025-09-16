"""Get document use case with company authorization."""

from dataclasses import dataclass
from typing import Optional, Protocol
from core.domain.entities.document import Document
from core.domain.entities.company import Company


class DocumentRepositoryProtocol(Protocol):
    """Protocol for document repository."""

    def find_by_id_and_company(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company."""
        ...


@dataclass
class GetDocumentInput:
    """Input data for getting a document."""
    document_id: int
    company: Company


@dataclass
class GetDocumentOutput:
    """Output data for getting a document."""
    document: Document


class DocumentNotFoundError(Exception):
    """Exception raised when document is not found or not authorized."""
    pass


class GetDocumentUseCase:
    """Use case for getting a document with company authorization."""

    def __init__(self, document_repository: DocumentRepositoryProtocol) -> None:
        self._document_repository = document_repository

    def execute(self, input_data: GetDocumentInput) -> GetDocumentOutput:
        """Execute the get document use case."""
        # Find document by ID and company to ensure authorization
        document = self._document_repository.find_by_id_and_company(
            document_id=input_data.document_id,
            company_id=input_data.company.id
        )

        if document is None:
            raise DocumentNotFoundError("Document not found or not authorized")

        return GetDocumentOutput(document=document)