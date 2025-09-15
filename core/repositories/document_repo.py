"""Document repository implementation."""

from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from core.domain.entities.document import Document
from core.orm.models import Document as DocumentModel
from core.orm.mappers import DocumentMapper


class DjangoDocumentRepository:
    """Django ORM implementation of DocumentRepository."""

    def save(self, document: Document) -> Document:
        """Save a document and return it with ID."""
        # Map entity to model
        model_data = {
            'company_id': document.company_id,
            'name': document.name,
            'token': document.token,
            'open_id': document.open_id,
            'status': document.status,
            'external_id': document.external_id,
            'created_by': document.created_by,
        }

        if document.id:
            # Update existing
            DocumentModel.objects.filter(id=document.id).update(**model_data)
            model = DocumentModel.objects.get(id=document.id)
        else:
            # Create new
            model = DocumentModel.objects.create(**model_data)

        # Map back to entity
        return DocumentMapper.to_entity(model)

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find a document by ID."""
        try:
            model = DocumentModel.objects.get(id=document_id)
            return DocumentMapper.to_entity(model)
        except ObjectDoesNotExist:
            return None

    def find_all(self) -> List[Document]:
        """Find all documents."""
        models = DocumentModel.objects.all().order_by('-id')
        return [DocumentMapper.to_entity(model) for model in models]

    def delete_by_id(self, document_id: int) -> bool:
        """Delete a document by ID."""
        deleted_count, _ = DocumentModel.objects.filter(id=document_id).delete()
        return deleted_count > 0

    def add_signers(self, document_id: int, signer_ids: List[int]) -> None:
        """Associate signers with a document."""
        document = DocumentModel.objects.get(id=document_id)
        document.signers.add(*signer_ids)