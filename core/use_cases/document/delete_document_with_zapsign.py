"""Delete document use case with ZapSign integration."""

from dataclasses import dataclass
from typing import Optional, Protocol
from core.domain.entities.document import Document
from core.domain.entities.company import Company
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class DocumentRepositoryProtocol(Protocol):
    """Protocol for document repository."""

    def find_by_id_including_deleted(self, document_id: int) -> Optional[Document]:
        """Find a document by ID, including soft deleted ones."""
        ...

    def save(self, document: Document) -> Document:
        """Save a document and return it with ID."""
        ...


class CompanyRepositoryProtocol(Protocol):
    """Protocol for company repository."""

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        ...


class ZapSignServiceProtocol(Protocol):
    """Protocol for ZapSign service."""

    def delete_document(self, api_token: str, doc_token: str) -> bool:
        """Delete a document in ZapSign API."""
        ...


@dataclass
class DeleteDocumentWithZapSignInput:
    """Input data for deleting a document with ZapSign integration."""
    document_id: int
    deleted_by: str


@dataclass
class DeleteDocumentWithZapSignOutput:
    """Output data for deleting a document with ZapSign integration."""
    document: Document
    success: bool
    zapsign_deleted: bool


class DocumentNotFoundError(Exception):
    """Exception raised when document is not found or not authorized."""
    pass


class DocumentAlreadyDeletedError(Exception):
    """Exception raised when document is already deleted."""
    pass


class DeleteDocumentWithZapSignUseCase:
    """Use case for deleting a document with ZapSign integration."""

    def __init__(
        self,
        document_repository: DocumentRepositoryProtocol,
        company_repository: CompanyRepositoryProtocol,
        zapsign_service: ZapSignServiceProtocol
    ) -> None:
        self._document_repository = document_repository
        self._company_repository = company_repository
        self._zapsign_service = zapsign_service

    def execute(self, input_data: DeleteDocumentWithZapSignInput) -> DeleteDocumentWithZapSignOutput:
        """Execute the delete document with ZapSign integration use case."""
        # Find document by ID (including soft deleted)
        document = self._document_repository.find_by_id_including_deleted(input_data.document_id)

        if document is None:
            raise DocumentNotFoundError("Document not found")

        # Check if document is already deleted
        if document.is_deleted:
            raise DocumentAlreadyDeletedError("Document is already deleted")

        # Get company information from document to retrieve API token
        if document.company_id is None:
            raise DocumentNotFoundError("Document has no associated company")

        company = self._company_repository.find_by_id(document.company_id)
        if company is None:
            raise DocumentNotFoundError("Associated company not found")

        # Delete from ZapSign first (if document has a token)
        zapsign_deleted = False
        if document.token:
            try:
                self._zapsign_service.delete_document(
                    api_token=company.api_token,
                    doc_token=document.token
                )
                zapsign_deleted = True
            except (ZapSignAuthenticationError, ZapSignValidationError, ZapSignAPIError) as e:
                # If ZapSign deletion fails, we might still want to soft delete locally
                # but this depends on business requirements. For now, we'll re-raise the error
                raise e

        # Perform soft delete with audit trail
        document.soft_delete(deleted_by=input_data.deleted_by)

        # Save the updated document
        updated_document = self._document_repository.save(document)

        return DeleteDocumentWithZapSignOutput(
            document=updated_document,
            success=True,
            zapsign_deleted=zapsign_deleted
        )