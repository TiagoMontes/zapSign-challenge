"""Remove signer from ZapSign use case."""

from dataclasses import dataclass
from typing import Optional, Protocol
from django.db import transaction

from core.domain.entities.signer import Signer
from core.domain.entities.company import Company
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class SignerRepositoryProtocol(Protocol):
    """Protocol for signer repository."""

    def find_by_id(self, signer_id: int) -> Optional[Signer]:
        """Find a signer by ID."""
        ...

    def delete_by_id(self, signer_id: int) -> bool:
        """Delete a signer by ID."""
        ...


class CompanyRepositoryProtocol(Protocol):
    """Protocol for company repository."""

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        ...


class ZapSignServiceProtocol(Protocol):
    """Protocol for ZapSign service."""

    def remove_signer(self, api_token: str, signer_token: str) -> bool:
        """Remove/delete a signer from ZapSign API."""
        ...


@dataclass
class RemoveSignerFromZapSignInput:
    """Input data for removing a signer from ZapSign."""
    signer_id: int


@dataclass
class RemoveSignerFromZapSignOutput:
    """Output data for removing a signer from ZapSign."""
    success: bool
    zapsign_removed: bool
    locally_removed: bool


class SignerNotFoundError(Exception):
    """Exception raised when signer is not found."""
    pass


class SignerRemovalError(Exception):
    """Exception raised when signer cannot be removed."""
    pass


class CompanyNotFoundError(Exception):
    """Exception raised when company is not found."""
    pass


class RemoveSignerFromZapSignUseCase:
    """Use case for removing a signer from ZapSign."""

    def __init__(
        self,
        signer_repository: SignerRepositoryProtocol,
        company_repository: CompanyRepositoryProtocol,
        zapsign_service: ZapSignServiceProtocol
    ) -> None:
        self._signer_repository = signer_repository
        self._company_repository = company_repository
        self._zapsign_service = zapsign_service

    @transaction.atomic
    def execute(self, input_data: RemoveSignerFromZapSignInput) -> RemoveSignerFromZapSignOutput:
        """Execute the remove signer from ZapSign use case."""
        # Find signer by ID
        signer = self._signer_repository.find_by_id(input_data.signer_id)

        if signer is None:
            raise SignerNotFoundError("Signer not found")

        # Check if signer has a token for ZapSign removal
        if not signer.token:
            raise SignerRemovalError("Signer has no token for ZapSign removal")

        # Get company information to retrieve API token
        if signer.company_id is None:
            raise CompanyNotFoundError("Signer has no associated company")

        company = self._company_repository.find_by_id(signer.company_id)
        if company is None:
            raise CompanyNotFoundError("Associated company not found")

        # Attempt to remove signer from ZapSign
        zapsign_removed = False
        try:
            zapsign_removed = self._zapsign_service.remove_signer(
                api_token=company.api_token,
                signer_token=signer.token
            )
        except ZapSignValidationError:
            # If signer doesn't exist in ZapSign, that's okay - continue with local removal
            zapsign_removed = False
        except (ZapSignAuthenticationError, ZapSignAPIError) as e:
            # Re-raise critical errors that should stop the process
            raise e

        # Attempt to remove signer locally
        locally_removed = self._signer_repository.delete_by_id(input_data.signer_id)

        # Consider success if at least one removal succeeded
        # or if both failed but for acceptable reasons
        success = zapsign_removed or locally_removed

        return RemoveSignerFromZapSignOutput(
            success=success,
            zapsign_removed=zapsign_removed,
            locally_removed=locally_removed
        )