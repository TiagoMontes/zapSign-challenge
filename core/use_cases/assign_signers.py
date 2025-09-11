from core.interfaces.repositories import IDocumentRepository


class AssignSignersUseCase:
    def __init__(self, document_repo: IDocumentRepository) -> None:
        self._document_repo = document_repo

    def execute(self, document_id: int, signer_ids: list[int]):
        if not signer_ids:
            return self._document_repo.get_by_id(document_id)
        return self._document_repo.assign_signers(document_id, signer_ids)

