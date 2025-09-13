from typing import Optional

from core.domain.entities.signer import Signer
from core.repositories.contracts import SignerRepositoryProtocol


class GetSignerUseCase:
    def __init__(self, signer_repo: SignerRepositoryProtocol) -> None:
        self._signer_repo = signer_repo

    def execute(self, signer_id: int) -> Optional[Signer]:
        return self._signer_repo.get_by_id(signer_id)