from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.document import Document as DocumentEntity
from core.orm.models import Document as DocumentModel
from core.orm.mappers import (
    document_model_to_entity,
    document_entity_to_model_data,
    map_documents,
)


class DocumentRepository:
    def create(self, document: DocumentEntity) -> DocumentEntity:
        obj = DocumentModel.objects.create(**document_entity_to_model_data(document))
        return document_model_to_entity(obj)

    def assign_signers(self, document_id: int, signer_ids: list[int]) -> DocumentEntity:
        obj = DocumentModel.objects.get(id=document_id)
        if signer_ids:
            obj.signers.set(list(signer_ids))
        return document_model_to_entity(obj)

    def get_by_id(self, document_id: int) -> Optional[DocumentEntity]:
        obj = DocumentModel.objects.filter(id=document_id).first()
        return document_model_to_entity(obj) if obj else None

    def list(self) -> Iterable[DocumentEntity]:
        return map_documents(DocumentModel.objects.order_by("-id").all())

    def delete(self, document_id: int) -> None:
        DocumentModel.objects.filter(id=document_id).delete()

