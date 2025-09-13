from typing import Optional

from core.domain.entities.document import Document
from core.repositories.contracts import DocumentRepositoryProtocol


class GetDocumentUseCase:
    def __init__(self, document_repo: DocumentRepositoryProtocol) -> None:
        self._document_repo = document_repo

    def execute(self, document_id: int) -> Optional[Document]:
        return self._document_repo.get_by_id(document_id)