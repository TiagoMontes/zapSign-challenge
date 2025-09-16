from __future__ import annotations

from typing import Any, Iterable, Union, TYPE_CHECKING
from django.db.models import QuerySet

if TYPE_CHECKING:
    # For type checking, import the models directly
    from .models import Company as CompanyModel, Document as DocumentModel, Signer as SignerModel, DocumentAnalysis as DocumentAnalysisModel

from core.domain.entities.company import Company as CompanyEntity
from core.domain.entities.document import Document as DocumentEntity
from core.domain.entities.signer import Signer as SignerEntity
from core.domain.entities.document_analysis import DocumentAnalysis as DocumentAnalysisEntity

if not TYPE_CHECKING:
    # At runtime, import normally
    from .models import Company as CompanyModel, Document as DocumentModel, Signer as SignerModel, DocumentAnalysis as DocumentAnalysisModel


def company_model_to_entity(obj: Any) -> CompanyEntity:
    return CompanyEntity(
        id=obj.id,
        name=str(obj.name),
        api_token=str(obj.api_token),
        created_at=obj.created_at,
        last_updated_at=obj.last_updated_at,
    )


def signer_model_to_entity(obj: Any) -> SignerEntity:
    return SignerEntity(
        id=obj.id,
        name=str(obj.name),
        email=str(obj.email),
        token=str(obj.token),
        status=str(obj.status),
        external_id=str(obj.external_id),
        created_at=getattr(obj, 'created_at', None),
        last_updated_at=getattr(obj, 'last_updated_at', None),
    )


def document_model_to_entity(obj: Any) -> DocumentEntity:
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
        is_deleted=getattr(obj, 'is_deleted', False),
        deleted_at=getattr(obj, 'deleted_at', None),
        deleted_by=getattr(obj, 'deleted_by', ''),
        # PDF processing fields
        pdf_url=getattr(obj, 'pdf_url', None),
        processing_status=getattr(obj, 'processing_status', 'UPLOADED'),
        checksum=getattr(obj, 'checksum', None),
        version_id=getattr(obj, 'version_id', None),
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
        "is_deleted": entity.is_deleted,
        "deleted_at": entity.deleted_at,
        "deleted_by": entity.deleted_by,
        # PDF processing fields
        "pdf_url": entity.pdf_url,
        "processing_status": entity.processing_status,
        "checksum": entity.checksum,
        "version_id": entity.version_id,
    }


def map_companies(objs: Union[QuerySet[CompanyModel], Iterable[CompanyModel]]) -> list[CompanyEntity]:
    return [company_model_to_entity(o) for o in objs]


def map_signers(objs: Union[QuerySet[SignerModel], Iterable[SignerModel]]) -> list[SignerEntity]:
    return [signer_model_to_entity(o) for o in objs]


def map_documents(objs: Union[QuerySet[DocumentModel], Iterable[DocumentModel]]) -> list[DocumentEntity]:
    return [document_model_to_entity(o) for o in objs]


class DocumentMapper:
    """Mapper for Document entities and models."""

    @staticmethod
    def to_entity(model: DocumentModel) -> DocumentEntity:
        """Convert Django model to domain entity."""
        return document_model_to_entity(model)

    @staticmethod
    def to_model_data(entity: DocumentEntity) -> dict:
        """Convert domain entity to model data."""
        return document_entity_to_model_data(entity)


class SignerMapper:
    """Mapper for Signer entities and models."""

    @staticmethod
    def to_entity(model: SignerModel) -> SignerEntity:
        """Convert Django model to domain entity."""
        return signer_model_to_entity(model)

    @staticmethod
    def to_model_data(entity: SignerEntity) -> dict:
        """Convert domain entity to model data."""
        return signer_entity_to_model_data(entity)


class CompanyMapper:
    """Mapper for Company entities and models."""

    @staticmethod
    def to_entity(model: CompanyModel) -> CompanyEntity:
        """Convert Django model to domain entity."""
        return company_model_to_entity(model)

    @staticmethod
    def to_model_data(entity: CompanyEntity) -> dict:
        """Convert domain entity to model data."""
        return company_entity_to_model_data(entity)


def document_analysis_model_to_entity(obj: Any) -> DocumentAnalysisEntity:
    """Convert DocumentAnalysis model to entity."""
    return DocumentAnalysisEntity(
        id=obj.id,
        document_id=obj.document_id,
        missing_topics=obj.missing_topics or [],
        summary=str(obj.summary),
        insights=obj.insights or [],
        analyzed_at=obj.analyzed_at,
    )


def document_analysis_entity_to_model_data(entity: DocumentAnalysisEntity) -> dict:
    """Convert DocumentAnalysis entity to model data."""
    return {
        "document_id": entity.document_id,
        "missing_topics": entity.missing_topics,
        "summary": entity.summary,
        "insights": entity.insights,
        "analyzed_at": entity.analyzed_at,
    }


def map_document_analyses(objs: Union[QuerySet[DocumentAnalysisModel], Iterable[DocumentAnalysisModel]]) -> list[DocumentAnalysisEntity]:
    """Map multiple DocumentAnalysis models to entities."""
    return [document_analysis_model_to_entity(o) for o in objs]


class DocumentAnalysisMapper:
    """Mapper for DocumentAnalysis entities and models."""

    @staticmethod
    def to_entity(model: DocumentAnalysisModel) -> DocumentAnalysisEntity:
        """Convert Django model to domain entity."""
        return document_analysis_model_to_entity(model)

    @staticmethod
    def to_model_data(entity: DocumentAnalysisEntity) -> dict:
        """Convert domain entity to model data."""
        return document_analysis_entity_to_model_data(entity)
