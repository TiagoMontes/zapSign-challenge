"""Signer provider for dependency injection."""

from functools import lru_cache

from core.services.zapsign_service import ZapSignService
from core.repositories.signer_repo import DjangoSignerRepository
from core.repositories.company_repo import CompanyRepository
from core.use_cases.signer.sync_signer_with_zapsign import SyncSignerWithZapSignUseCase
from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignUseCase
from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignUseCase


class SignerProvider:
    """Provider for signer-related dependencies using singleton pattern."""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_zapsign_service() -> ZapSignService:
        """Get ZapSign service instance (singleton)."""
        return ZapSignService()

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
    def get_sync_signer_with_zapsign_use_case() -> SyncSignerWithZapSignUseCase:
        """
        Get configured SyncSignerWithZapSignUseCase.

        Note: Use case is not cached as it might need different configurations.
        Dependencies are singleton to ensure consistency.
        """
        return SyncSignerWithZapSignUseCase(
            signer_repository=SignerProvider.get_signer_repository(),
            company_repository=SignerProvider.get_company_repository(),
            zapsign_service=SignerProvider.get_zapsign_service(),
        )

    @staticmethod
    def get_update_signer_in_zapsign_use_case() -> UpdateSignerInZapSignUseCase:
        """
        Get configured UpdateSignerInZapSignUseCase.

        Note: Use case is not cached as it might need different configurations.
        Dependencies are singleton to ensure consistency.
        """
        return UpdateSignerInZapSignUseCase(
            signer_repository=SignerProvider.get_signer_repository(),
            company_repository=SignerProvider.get_company_repository(),
            zapsign_service=SignerProvider.get_zapsign_service(),
        )

    @staticmethod
    def get_remove_signer_from_zapsign_use_case() -> RemoveSignerFromZapSignUseCase:
        """
        Get configured RemoveSignerFromZapSignUseCase.

        Note: Use case is not cached as it might need different configurations.
        Dependencies are singleton to ensure consistency.
        """
        return RemoveSignerFromZapSignUseCase(
            signer_repository=SignerProvider.get_signer_repository(),
            company_repository=SignerProvider.get_company_repository(),
            zapsign_service=SignerProvider.get_zapsign_service(),
        )

    @staticmethod
    def clear_cache():
        """
        Clear all cached singleton instances.

        This is useful for testing purposes to reset the DI container state.
        """
        SignerProvider.get_zapsign_service.cache_clear()
        SignerProvider.get_signer_repository.cache_clear()
        SignerProvider.get_company_repository.cache_clear()