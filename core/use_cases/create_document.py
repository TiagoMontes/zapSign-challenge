from core.entities.document import Document
from core.interfaces.dtos import CreateDocumentDTO, DocumentResponseDTO
from core.interfaces.repositories import IDocumentRepository


class CreateDocumentUseCase:
    def __init__(self, document_repo: IDocumentRepository) -> None:
        self._document_repo = document_repo

    def execute(self, data: CreateDocumentDTO) -> DocumentResponseDTO:
        # Validate via entity
        Document(
            id=None,
            company_id=data.company_id,
            name=data.name,
            signer_ids=list(data.signer_ids or []),
        )
        created = self._document_repo.create(data)
        if data.signer_ids:
            created = self._document_repo.assign_signers(created.id, list(data.signer_ids))
        return created

