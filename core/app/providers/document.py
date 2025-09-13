from __future__ import annotations

from core.repositories import DocumentRepository as DjangoDocumentRepository
from core.repositories.contracts import DocumentRepositoryProtocol
from core.use_cases.signer.assign_signers import AssignSignersUseCase
from core.use_cases.document.create_document import CreateDocumentUseCase
from core.use_cases.document.list_documents import ListDocumentsUseCase
from core.use_cases.document.get_document import GetDocumentUseCase
from core.use_cases.document.delete_document import DeleteDocumentUseCase


def get_document_repository() -> DocumentRepositoryProtocol:
    return DjangoDocumentRepository()


def get_create_document_use_case() -> CreateDocumentUseCase:
    return CreateDocumentUseCase(get_document_repository())


def get_list_documents_use_case() -> ListDocumentsUseCase:
    return ListDocumentsUseCase(get_document_repository())


def get_get_document_use_case() -> GetDocumentUseCase:
    return GetDocumentUseCase(get_document_repository())


def get_delete_document_use_case() -> DeleteDocumentUseCase:
    return DeleteDocumentUseCase(get_document_repository())


def get_assign_signers_use_case() -> AssignSignersUseCase:
    return AssignSignersUseCase(get_document_repository())
