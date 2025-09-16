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
        # Map entity to model using the mapper
        model_data = DocumentMapper.to_model_data(document)

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

    def find_by_id_and_company(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company."""
        try:
            model = DocumentModel.objects.get(
                id=document_id,
                company_id=company_id,
                is_deleted=False
            )
            return DocumentMapper.to_entity(model)
        except ObjectDoesNotExist:
            return None

    def find_by_id_and_company_including_deleted(self, document_id: int, company_id: int) -> Optional[Document]:
        """Find a document by ID that belongs to a specific company, including soft deleted ones."""
        try:
            model = DocumentModel.objects.get(
                id=document_id,
                company_id=company_id
            )
            return DocumentMapper.to_entity(model)
        except ObjectDoesNotExist:
            return None

    def find_by_company(self, company_id: int, include_deleted: bool = False) -> List[Document]:
        """Find all documents belonging to a specific company."""
        if include_deleted:
            models = DocumentModel.objects.filter(company_id=company_id).order_by('-id')
        else:
            models = DocumentModel.objects.filter(
                company_id=company_id,
                is_deleted=False
            ).order_by('-id')
        return [DocumentMapper.to_entity(model) for model in models]

    def find_all(self) -> List[Document]:
        """Find all documents (excluding soft deleted)."""
        models = DocumentModel.objects.filter(is_deleted=False).order_by('-id')
        return [DocumentMapper.to_entity(model) for model in models]

    def delete_by_id(self, document_id: int) -> bool:
        """Hard delete a document by ID."""
        deleted_count, _ = DocumentModel.objects.filter(id=document_id).delete()
        return deleted_count > 0

    def soft_delete_by_id(self, document_id: int, deleted_by: str) -> bool:
        """Soft delete a document by ID."""
        try:
            document = self.find_by_id(document_id)
            if document and not document.is_deleted:
                document.soft_delete(deleted_by)
                self.save(document)
                return True
            return False
        except ObjectDoesNotExist:
            return False

    def add_signers(self, document_id: int, signer_ids: List[int]) -> None:
        """Associate signers with a document."""
        document = DocumentModel.objects.get(id=document_id)
        document.signers.add(*signer_ids)