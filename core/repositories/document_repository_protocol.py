from typing import Protocol, Optional, List
from core.domain.entities.document import Document


class DocumentRepositoryProtocol(Protocol):
    """Protocol defining the interface for Document repositories."""

    def save(self, document: Document) -> Document:
        """Save a document entity."""
        ...

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find a document by ID."""
        ...

    def find_by_id_including_deleted(self, document_id: int) -> Optional[Document]:
        """Find a document by ID, including soft deleted ones."""
        ...

    def find_by_id_and_company(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company."""
        ...

    def find_by_id_and_company_including_deleted(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company, including soft deleted ones."""
        ...

    def find_by_company(self, company_id: int, include_deleted: bool = False) -> List[Document]:
        """Find all documents belonging to a specific company."""
        ...

    def find_all(self) -> List[Document]:
        """Find all documents."""
        ...

    def delete_by_id(self, document_id: int) -> bool:
        """Hard delete a document by ID."""
        ...

    def soft_delete_by_id(self, document_id: int, deleted_by: str) -> bool:
        """Soft delete a document by ID."""
        ...

    def add_signers(self, document_id: int, signer_ids: List[int]) -> None:
        """Associate signers with a document."""
        ...