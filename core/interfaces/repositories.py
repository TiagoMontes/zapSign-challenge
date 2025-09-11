from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from .dtos import (
    CompanyDTO,
    CreateCompanyDTO,
    CreateDocumentDTO,
    CreateSignerDTO,
    DocumentResponseDTO,
    SignerDTO,
)


class ICompanyRepository(ABC):
    @abstractmethod
    def create(self, data: CreateCompanyDTO) -> CompanyDTO: ...

    @abstractmethod
    def get_by_id(self, company_id: int) -> Optional[CompanyDTO]: ...

    @abstractmethod
    def list(self) -> Iterable[CompanyDTO]: ...

    @abstractmethod
    def delete(self, company_id: int) -> None: ...


class ISignerRepository(ABC):
    @abstractmethod
    def create(self, data: CreateSignerDTO) -> SignerDTO: ...

    @abstractmethod
    def get_by_id(self, signer_id: int) -> Optional[SignerDTO]: ...

    @abstractmethod
    def list(self) -> Iterable[SignerDTO]: ...


class IDocumentRepository(ABC):
    @abstractmethod
    def create(self, data: CreateDocumentDTO) -> DocumentResponseDTO: ...

    @abstractmethod
    def assign_signers(self, document_id: int, signer_ids: list[int]) -> DocumentResponseDTO: ...

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[DocumentResponseDTO]: ...

    @abstractmethod
    def list(self) -> Iterable[DocumentResponseDTO]: ...

