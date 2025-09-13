from typing import Optional

from core.domain.entities.document import Document
from core.repositories.contracts import DocumentRepositoryProtocol


class AssignSignersUseCase:
    def __init__(self, document_repo: DocumentRepositoryProtocol) -> None:
        self._document_repo = document_repo

    def execute(self, document_id: int, signer_ids: list[int]) -> Optional[Document]:
        if not signer_ids:
            return self._document_repo.get_by_id(document_id)
        return self._document_repo.assign_signers(document_id, signer_ids)
