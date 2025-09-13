from __future__ import annotations

from django.db import transaction

from core.repositories.contracts import DocumentRepositoryProtocol


class DeleteDocumentUseCase:
    def __init__(self, document_repo: DocumentRepositoryProtocol) -> None:
        self._document_repo = document_repo

    def execute(self, document_id: int) -> None:
        with transaction.atomic():  # type: ignore[attr-defined]
            self._document_repo.delete(document_id)