from __future__ import annotations

from typing import Iterable

from core.domain.entities.company import Company as CompanyEntity
from core.domain.entities.document import Document as DocumentEntity
from core.domain.entities.signer import Signer as SignerEntity
from .models import Company as CompanyModel, Document as DocumentModel, Signer as SignerModel


def company_model_to_entity(obj: CompanyModel) -> CompanyEntity:
    return CompanyEntity(id=obj.id, name=str(obj.name), api_token=str(obj.api_token))


def signer_model_to_entity(obj: SignerModel) -> SignerEntity:
    return SignerEntity(
        id=obj.id,
        name=str(obj.name),
        email=str(obj.email),
        token=str(obj.token),
        status=str(obj.status),
        external_id=str(obj.external_id),
    )


def document_model_to_entity(obj: DocumentModel) -> DocumentEntity:
    signer_ids = list(obj.signers.values_list("id", flat=True)) if obj.id else []
    return DocumentEntity(
        id=obj.id,
        company_id=obj.company_id,
        name=str(obj.name),
        status=str(obj.status),
        token=str(obj.token),
        open_id=obj.open_id,
        external_id=str(obj.external_id),
        created_by=str(obj.created_by),
        created_at=obj.created_at,
        last_updated_at=obj.last_updated_at,
        signer_ids=signer_ids,
    )


def company_entity_to_model_data(entity: CompanyEntity) -> dict:
    return {"name": entity.name, "api_token": entity.api_token}


def signer_entity_to_model_data(entity: SignerEntity) -> dict:
    return {
        "name": entity.name,
        "email": entity.email,
        "token": entity.token,
        "status": entity.status,
        "external_id": entity.external_id,
    }


def document_entity_to_model_data(entity: DocumentEntity) -> dict:
    return {
        "company_id": entity.company_id,
        "name": entity.name,
        "external_id": entity.external_id,
        "created_by": entity.created_by,
        "status": entity.status,
        "token": entity.token,
        "open_id": entity.open_id,
    }


def map_companies(objs: Iterable[CompanyModel]) -> list[CompanyEntity]:
    return [company_model_to_entity(o) for o in objs]


def map_signers(objs: Iterable[SignerModel]) -> list[SignerEntity]:
    return [signer_model_to_entity(o) for o in objs]


def map_documents(objs: Iterable[DocumentModel]) -> list[DocumentEntity]:
    return [document_model_to_entity(o) for o in objs]

