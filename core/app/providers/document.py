from __future__ import annotations

from core.repositories import DocumentRepository
from core.use_cases.assign_signers import AssignSignersUseCase
from core.use_cases.create_document import CreateDocumentUseCase


def get_document_repository() -> DocumentRepository:
    return DocumentRepository()


def get_create_document_use_case() -> CreateDocumentUseCase:
    return CreateDocumentUseCase(get_document_repository())


def get_assign_signers_use_case() -> AssignSignersUseCase:
    return AssignSignersUseCase(get_document_repository())
