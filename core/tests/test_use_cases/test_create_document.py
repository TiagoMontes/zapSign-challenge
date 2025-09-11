from django.test import SimpleTestCase

from core.interfaces.dtos import CreateDocumentDTO, DocumentResponseDTO
from core.interfaces.repositories import IDocumentRepository
from core.use_cases.create_document import CreateDocumentUseCase


class InMemoryDocumentRepo(IDocumentRepository):
    def __init__(self) -> None:
        self._seq = 0
        self.created = []
        self.assigned = {}

    def create(self, data: CreateDocumentDTO) -> DocumentResponseDTO:
        self._seq += 1
        dto = DocumentResponseDTO(
            id=self._seq,
            company_id=data.company_id,
            name=data.name,
            status="",
            token="",
            open_id=None,
            external_id=data.external_id,
        )
        self.created.append(dto)
        return dto

    def assign_signers(self, document_id: int, signer_ids: list[int]) -> DocumentResponseDTO:
        self.assigned[document_id] = list(signer_ids)
        # return the existing document dto (simple emulation)
        for d in self.created:
            if d.id == document_id:
                return d
        raise AssertionError("Document not found in repo")

    def get_by_id(self, document_id: int):
        return next((d for d in self.created if d.id == document_id), None)

    def list(self):
        return list(self.created)


class CreateDocumentUseCaseTests(SimpleTestCase):
    def test_create_document_assigns_signers_when_provided(self):
        repo = InMemoryDocumentRepo()
        uc = CreateDocumentUseCase(repo)
        result = uc.execute(CreateDocumentDTO(company_id=1, name="Doc", signer_ids=[10, 20]))
        self.assertEqual(result.id, 1)
        self.assertEqual(repo.assigned[1], [10, 20])

    def test_create_document_without_signers_does_not_assign(self):
        repo = InMemoryDocumentRepo()
        uc = CreateDocumentUseCase(repo)
        result = uc.execute(CreateDocumentDTO(company_id=1, name="Doc"))
        self.assertEqual(result.id, 1)
        self.assertEqual(repo.assigned, {})

