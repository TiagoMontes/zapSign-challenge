"""Fake document repository for testing."""

from typing import List, Optional, Dict
from core.domain.entities.document import Document


class FakeDocumentRepository:
    """Fake implementation of DocumentRepository for testing."""

    def __init__(self) -> None:
        self._documents: Dict[int, Document] = {}
        self._next_id = 1

    def save(self, document: Document) -> Document:
        """Save a document and return it with ID."""
        if document.id is None:
            document.id = self._next_id
            self._next_id += 1

        self._documents[document.id] = document
        return document

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find a document by ID."""
        return self._documents.get(document_id)

    def find_by_id_including_deleted(self, document_id: int) -> Optional[Document]:
        """Find a document by ID, including soft deleted ones."""
        return self._documents.get(document_id)

    def find_by_id_and_company(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company."""
        document = self._documents.get(document_id)
        if document and document.company_id == company_id and not document.is_deleted:
            return document
        return None

    def find_by_id_and_company_including_deleted(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company, including soft deleted ones."""
        document = self._documents.get(document_id)
        if document and document.company_id == company_id:
            return document
        return None

    def find_by_company(self, company_id: int, include_deleted: bool = False) -> List[Document]:
        """Find all documents belonging to a specific company."""
        documents = []
        for document in self._documents.values():
            if document.company_id == company_id:
                if include_deleted or not document.is_deleted:
                    documents.append(document)
        return sorted(documents, key=lambda d: d.id or 0, reverse=True)

    def find_all(self) -> List[Document]:
        """Find all documents."""
        return list(self._documents.values())

    def delete_by_id(self, document_id: int) -> bool:
        """Hard delete a document by ID."""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    def soft_delete_by_id(self, document_id: int, deleted_by: str) -> bool:
        """Soft delete a document by ID."""
        document = self._documents.get(document_id)
        if document and not document.is_deleted:
            document.soft_delete(deleted_by)
            return True
        return False

    def add_signers(self, document_id: int, signer_ids: List[int]) -> None:
        """Associate signers with a document."""
        document = self._documents.get(document_id)
        if document:
            for signer_id in signer_ids:
                document.add_signer(signer_id)

    def clear(self) -> None:
        """Clear all documents (for testing)."""
        self._documents.clear()
        self._next_id = 1