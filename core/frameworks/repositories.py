from __future__ import annotations

from typing import Iterable, Optional

from core.interfaces.dtos import (
    CompanyDTO,
    CreateCompanyDTO,
    CreateDocumentDTO,
    CreateSignerDTO,
    DocumentResponseDTO,
    SignerDTO,
)
from core.interfaces.repositories import (
    ICompanyRepository,
    IDocumentRepository,
    ISignerRepository,
)
from .django.models import Company, Document, Signer


def _company_to_dto(obj: Company) -> CompanyDTO:
    return CompanyDTO(id=obj.id, name=obj.name, api_token=obj.api_token)


def _signer_to_dto(obj: Signer) -> SignerDTO:
    return SignerDTO(
        id=obj.id,
        name=obj.name,
        email=obj.email,
        token=obj.token,
        status=obj.status,
        external_id=obj.external_id,
    )


def _document_to_dto(obj: Document) -> DocumentResponseDTO:
    return DocumentResponseDTO(
        id=obj.id,
        company_id=obj.company_id,
        name=obj.name,
        status=obj.status,
        token=obj.token,
        open_id=obj.open_id,
        external_id=obj.external_id,
    )


class CompanyRepository(ICompanyRepository):
    def create(self, data: CreateCompanyDTO) -> CompanyDTO:
        obj = Company.objects.create(name=data.name, api_token=data.api_token)
        return _company_to_dto(obj)

    def get_by_id(self, company_id: int) -> Optional[CompanyDTO]:
        obj = Company.objects.filter(id=company_id).first()
        return _company_to_dto(obj) if obj else None

    def list(self) -> Iterable[CompanyDTO]:
        return [_company_to_dto(o) for o in Company.objects.order_by("-id").all()]

    def delete(self, company_id: int) -> None:
        Company.objects.filter(id=company_id).delete()


class SignerRepository(ISignerRepository):
    def create(self, data: CreateSignerDTO) -> SignerDTO:
        obj = Signer.objects.create(name=data.name, email=data.email, external_id=data.external_id)
        return _signer_to_dto(obj)

    def get_by_id(self, signer_id: int) -> Optional[SignerDTO]:
        obj = Signer.objects.filter(id=signer_id).first()
        return _signer_to_dto(obj) if obj else None

    def list(self) -> Iterable[SignerDTO]:
        return [_signer_to_dto(o) for o in Signer.objects.order_by("-id").all()]


class DocumentRepository(IDocumentRepository):
    def create(self, data: CreateDocumentDTO) -> DocumentResponseDTO:
        obj = Document.objects.create(
            company_id=data.company_id,
            name=data.name,
            external_id=data.external_id,
            created_by=data.created_by,
        )
        return _document_to_dto(obj)

    def assign_signers(self, document_id: int, signer_ids: list[int]) -> DocumentResponseDTO:
        obj = Document.objects.get(id=document_id)
        if signer_ids:
            obj.signers.set(list(signer_ids))
        return _document_to_dto(obj)

    def get_by_id(self, document_id: int) -> Optional[DocumentResponseDTO]:
        obj = Document.objects.filter(id=document_id).first()
        return _document_to_dto(obj) if obj else None

    def list(self) -> Iterable[DocumentResponseDTO]:
        return [_document_to_dto(o) for o in Document.objects.order_by("-id").all()]

