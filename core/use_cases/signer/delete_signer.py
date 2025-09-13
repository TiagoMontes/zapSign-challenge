from __future__ import annotations

from django.db import transaction

from core.repositories.contracts import SignerRepositoryProtocol


class DeleteSignerUseCase:
    def __init__(self, signer_repo: SignerRepositoryProtocol) -> None:
        self._signer_repo = signer_repo

    def execute(self, signer_id: int) -> None:
        with transaction.atomic():  # type: ignore[attr-defined]
            self._signer_repo.delete(signer_id)