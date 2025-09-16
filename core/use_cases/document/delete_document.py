"""Soft delete document use case with audit trail."""

from dataclasses import dataclass
from typing import Optional, Protocol
from core.domain.entities.document import Document
from core.domain.entities.company import Company


class DocumentRepositoryProtocol(Protocol):
    """Protocol for document repository."""

    def find_by_id_and_company_including_deleted(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company, including soft deleted ones."""
        ...

    def save(self, document: Document) -> Document:
        """Save a document and return it with ID."""
        ...


@dataclass
class DeleteDocumentInput:
    """Input data for soft deleting a document."""
    document_id: int
    company: Company
    deleted_by: str


@dataclass
class DeleteDocumentOutput:
    """Output data for soft deleting a document."""
    document: Document
    success: bool


class DocumentNotFoundError(Exception):
    """Exception raised when document is not found or not authorized."""
    pass


class DocumentAlreadyDeletedError(Exception):
    """Exception raised when document is already deleted."""
    pass


class SoftDeleteDocumentUseCase:
    """Use case for soft deleting a document with audit trail."""

    def __init__(self, document_repository: DocumentRepositoryProtocol) -> None:
        self._document_repository = document_repository

    def execute(self, input_data: DeleteDocumentInput) -> DeleteDocumentOutput:
        """Execute the soft delete document use case."""
        # Find document by ID and company to ensure authorization (including soft deleted)
        document = self._document_repository.find_by_id_and_company_including_deleted(
            document_id=input_data.document_id,
            company_id=input_data.company.id
        )

        if document is None:
            raise DocumentNotFoundError("Document not found or not authorized")

        # Check if document is already deleted
        if document.is_deleted:
            raise DocumentAlreadyDeletedError("Document is already deleted")

        # Perform soft delete with audit trail
        document.soft_delete(deleted_by=input_data.deleted_by)

        # Save the updated document
        updated_document = self._document_repository.save(document)

        return DeleteDocumentOutput(
            document=updated_document,
            success=True
        )