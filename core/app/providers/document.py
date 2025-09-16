"""Document provider for dependency injection."""

from functools import lru_cache

from core.services.zapsign_service import ZapSignService
from core.services.pdf.pdf_service import PDFService
from core.repositories.document_repo import DjangoDocumentRepository
from core.repositories.signer_repo import DjangoSignerRepository
from core.repositories.company_repo import CompanyRepository
from core.use_cases.document.create_document_from_upload import CreateDocumentFromUploadUseCase
from core.use_cases.document.list_documents import ListDocumentsUseCase
from core.use_cases.document.get_document import GetDocumentUseCase
from core.use_cases.document.delete_document import SoftDeleteDocumentUseCase
from core.use_cases.document.delete_document_with_zapsign import DeleteDocumentWithZapSignUseCase


class DocumentProvider:
    """Provider for document-related dependencies using singleton pattern."""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_zapsign_service() -> ZapSignService:
        """Get ZapSign service instance (singleton)."""
        return ZapSignService()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_document_repository() -> DjangoDocumentRepository:
        """Get document repository instance (singleton)."""
        return DjangoDocumentRepository()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_signer_repository() -> DjangoSignerRepository:
        """Get signer repository instance (singleton)."""
        return DjangoSignerRepository()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_company_repository() -> CompanyRepository:
        """Get company repository instance (singleton)."""
        return CompanyRepository()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_pdf_service() -> PDFService:
        """Get PDF service instance (singleton)."""
        return PDFService()

    @staticmethod
    def get_create_document_use_case() -> CreateDocumentFromUploadUseCase:
        """
        Get configured CreateDocumentFromUploadUseCase.

        Note: Use case is not cached as it might need different configurations.
        Dependencies are singleton to ensure consistency.
        """
        return CreateDocumentFromUploadUseCase(
            zapsign_service=DocumentProvider.get_zapsign_service(),
            document_repository=DocumentProvider.get_document_repository(),
            signer_repository=DocumentProvider.get_signer_repository(),
            pdf_service=DocumentProvider.get_pdf_service(),
        )

    @staticmethod
    def get_list_documents_use_case() -> ListDocumentsUseCase:
        """Get configured ListDocumentsUseCase."""
        return ListDocumentsUseCase(
            document_repository=DocumentProvider.get_document_repository()
        )

    @staticmethod
    def get_get_document_use_case() -> GetDocumentUseCase:
        """Get configured GetDocumentUseCase."""
        return GetDocumentUseCase(
            document_repository=DocumentProvider.get_document_repository()
        )

    @staticmethod
    def get_soft_delete_document_use_case() -> SoftDeleteDocumentUseCase:
        """Get configured SoftDeleteDocumentUseCase."""
        return SoftDeleteDocumentUseCase(
            document_repository=DocumentProvider.get_document_repository()
        )

    @staticmethod
    def get_delete_document_with_zapsign_use_case() -> DeleteDocumentWithZapSignUseCase:
        """Get configured DeleteDocumentWithZapSignUseCase."""
        return DeleteDocumentWithZapSignUseCase(
            document_repository=DocumentProvider.get_document_repository(),
            company_repository=DocumentProvider.get_company_repository(),
            zapsign_service=DocumentProvider.get_zapsign_service()
        )

    @staticmethod
    def clear_cache():
        """
        Clear all cached singleton instances.

        This is useful for testing purposes to reset the DI container state.
        """
        DocumentProvider.get_zapsign_service.cache_clear()
        DocumentProvider.get_document_repository.cache_clear()
        DocumentProvider.get_signer_repository.cache_clear()
        DocumentProvider.get_company_repository.cache_clear()
        DocumentProvider.get_pdf_service.cache_clear()
