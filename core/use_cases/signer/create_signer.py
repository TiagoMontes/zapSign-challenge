from core.domain.entities.signer import Signer
from core.repositories.contracts import SignerRepositoryProtocol


class CreateSignerUseCase:
    def __init__(self, signer_repo: SignerRepositoryProtocol) -> None:
        self._signer_repo = signer_repo

    def execute(self, signer: Signer) -> Signer:
        # Basic entity-level validation happens on Signer
        _ = Signer(id=None, name=signer.name, email=signer.email)
        return self._signer_repo.create(signer)