from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.document import Document


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._seq = 0
        self._docs: dict[int, Document] = {}

    def create(self, document: Document) -> Document:
        self._seq += 1
        doc = Document(
            id=self._seq,
            company_id=document.company_id,
            name=document.name,
            status=document.status,
            token=document.token,
            open_id=document.open_id,
            created_by=document.created_by,
            external_id=document.external_id,
            signer_ids=list(document.signer_ids or []),
        )
        self._docs[self._seq] = doc
        return doc

    def assign_signers(self, document_id: int, signer_ids: list[int]) -> Document:
        doc = self._docs[document_id]
        doc.signer_ids = list(signer_ids)
        return doc

    def get_by_id(self, document_id: int) -> Optional[Document]:
        return self._docs.get(document_id)

    def list(self) -> Iterable[Document]:
        return list(self._docs.values())

    def delete(self, document_id: int) -> None:
        self._docs.pop(document_id, None)

