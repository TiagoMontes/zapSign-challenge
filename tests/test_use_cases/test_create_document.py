from __future__ import annotations

from django.test import SimpleTestCase

from core.domain.entities.document import Document
from tests.fakes.document_repo import InMemoryDocumentRepository
from core.use_cases.document.create_document import CreateDocumentUseCase


class CreateDocumentUseCaseTests(SimpleTestCase):
    def test_create_document_assigns_signers_when_provided(self) -> None:
        repo = InMemoryDocumentRepository()
        uc = CreateDocumentUseCase(repo)
        result = uc.execute(Document(company_id=1, name="Doc", signer_ids=[10, 20]))
        self.assertEqual(result.id, 1)
        # The repository sets signer_ids on the stored entity
        self.assertEqual(result.signer_ids, [10, 20])

    def test_create_document_without_signers_does_not_assign(self) -> None:
        repo = InMemoryDocumentRepository()
        uc = CreateDocumentUseCase(repo)
        result = uc.execute(Document(company_id=1, name="Doc"))
        self.assertEqual(result.id, 1)
        self.assertEqual(result.signer_ids, [])

