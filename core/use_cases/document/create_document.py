from __future__ import annotations

from django.db import transaction

from core.domain.entities.document import Document
from core.repositories.contracts import DocumentRepositoryProtocol


class CreateDocumentUseCase:
    def __init__(self, document_repo: DocumentRepositoryProtocol) -> None:
        self._document_repo = document_repo

    def execute(self, document: Document) -> Document:
        # Validation already occurs in Document.__post_init__ when entity is created
        with transaction.atomic():  # type: ignore[attr-defined]
            created = self._document_repo.create(document)
            if document.signer_ids:
                created = self._document_repo.assign_signers(created.id or 0, list(document.signer_ids))
            return created
