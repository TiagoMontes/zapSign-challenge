"""Repository contracts/interfaces."""

from typing import Protocol, Optional, List
from core.domain.entities.document import Document
from core.domain.entities.signer import Signer


class DocumentRepository(Protocol):
    """Protocol for Document repository."""

    def save(self, document: Document) -> Document:
        """Save a document and return it with ID."""
        ...

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find a document by ID."""
        ...

    def find_all(self) -> List[Document]:
        """Find all documents."""
        ...

    def delete_by_id(self, document_id: int) -> bool:
        """Delete a document by ID."""
        ...

    def add_signers(self, document_id: int, signer_ids: List[int]) -> None:
        """Associate signers with a document."""
        ...


class SignerRepository(Protocol):
    """Protocol for Signer repository."""

    def save(self, signer: Signer) -> Signer:
        """Save a signer and return it with ID."""
        ...

    def save_bulk(self, signers: List[Signer]) -> List[Signer]:
        """Save multiple signers and return them with IDs."""
        ...

    def find_by_id(self, signer_id: int) -> Optional[Signer]:
        """Find a signer by ID."""
        ...

    def find_all(self) -> List[Signer]:
        """Find all signers."""
        ...

    def delete_by_id(self, signer_id: int) -> bool:
        """Delete a signer by ID."""
        ...