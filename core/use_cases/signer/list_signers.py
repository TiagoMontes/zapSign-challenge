from typing import Iterable

from core.domain.entities.signer import Signer
from core.repositories.contracts import SignerRepositoryProtocol


class ListSignersUseCase:
    def __init__(self, signer_repo: SignerRepositoryProtocol) -> None:
        self._signer_repo = signer_repo

    def execute(self) -> Iterable[Signer]:
        return self._signer_repo.list()