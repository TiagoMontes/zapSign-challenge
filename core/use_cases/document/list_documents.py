from typing import Iterable

from core.domain.entities.document import Document
from core.repositories.contracts import DocumentRepositoryProtocol


class ListDocumentsUseCase:
    def __init__(self, document_repo: DocumentRepositoryProtocol) -> None:
        self._document_repo = document_repo

    def execute(self) -> Iterable[Document]:
        return self._document_repo.list()