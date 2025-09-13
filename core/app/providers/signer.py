from __future__ import annotations

from core.repositories import SignerRepository as DjangoSignerRepository
from core.repositories.contracts import SignerRepositoryProtocol
from core.use_cases.signer.create_signer import CreateSignerUseCase
from core.use_cases.signer.list_signers import ListSignersUseCase
from core.use_cases.signer.get_signer import GetSignerUseCase
from core.use_cases.signer.delete_signer import DeleteSignerUseCase


def get_signer_repository() -> SignerRepositoryProtocol:
    return DjangoSignerRepository()


def get_create_signer_use_case() -> CreateSignerUseCase:
    return CreateSignerUseCase(get_signer_repository())


def get_list_signers_use_case() -> ListSignersUseCase:
    return ListSignersUseCase(get_signer_repository())


def get_get_signer_use_case() -> GetSignerUseCase:
    return GetSignerUseCase(get_signer_repository())


def get_delete_signer_use_case() -> DeleteSignerUseCase:
    return DeleteSignerUseCase(get_signer_repository())