from core.domain.entities.document import Document
from core.repositories.document_repo import DocumentRepository


class CreateDocumentUseCase:
    def __init__(self, document_repo: DocumentRepository) -> None:
        self._document_repo = document_repo

    def execute(self, document: Document) -> Document:
        # Validation happens in Document.__post_init__
        _ = Document(
            id=document.id,
            company_id=document.company_id,
            name=document.name,
            signer_ids=list(document.signer_ids or []),
            status=document.status,
            token=document.token,
            open_id=document.open_id,
            created_by=document.created_by,
            external_id=document.external_id,
            created_at=document.created_at,
            last_updated_at=document.last_updated_at,
        )
        created = self._document_repo.create(document)
        if document.signer_ids:
            created = self._document_repo.assign_signers(created.id or 0, list(document.signer_ids))
        return created
