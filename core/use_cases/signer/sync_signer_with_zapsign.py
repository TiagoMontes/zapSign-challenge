"""Sync signer with ZapSign use case."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from django.db import transaction

from core.domain.entities.signer import Signer
from core.domain.entities.company import Company
from core.domain.value_objects.zapsign_response import ZapSignSignerResponse
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

    def save(self, signer: Signer) -> Signer:
        """Save a signer and return it with ID."""
        ...


class CompanyRepositoryProtocol(Protocol):
    """Protocol for company repository."""

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        ...


class ZapSignServiceProtocol(Protocol):
    """Protocol for ZapSign service."""

    def get_signer_by_token(self, api_token: str, signer_token: str) -> ZapSignSignerResponse:
        """Get a signer by token from ZapSign API."""
        ...


@dataclass
class SyncSignerWithZapSignInput:
    """Input data for syncing a signer with ZapSign."""
    signer_id: int


@dataclass
class SyncSignerWithZapSignOutput:
    """Output data for syncing a signer with ZapSign."""
    signer: Signer
    success: bool


class SignerNotFoundError(Exception):
    """Exception raised when signer is not found."""
    pass


class SignerSyncError(Exception):
    """Exception raised when signer cannot be synced."""
    pass


class CompanyNotFoundError(Exception):
    """Exception raised when company is not found."""
    pass


class SyncSignerWithZapSignUseCase:
    """Use case for syncing a signer with ZapSign."""

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
    def execute(self, input_data: SyncSignerWithZapSignInput) -> SyncSignerWithZapSignOutput:
        """Execute the sync signer with ZapSign use case."""
        # Find signer by ID
        signer = self._signer_repository.find_by_id(input_data.signer_id)

        if signer is None:
            raise SignerNotFoundError("Signer not found")

        # Check if signer has a token for ZapSign sync
        if not signer.token:
            raise SignerSyncError("Signer has no token for ZapSign sync")

        # Get company information to retrieve API token
        if signer.company_id is None:
            raise CompanyNotFoundError("Signer has no associated company")

        company = self._company_repository.find_by_id(signer.company_id)
        if company is None:
            raise CompanyNotFoundError("Associated company not found")

        # Fetch signer data from ZapSign
        try:
            zapsign_signer_data = self._zapsign_service.get_signer_by_token(
                api_token=company.api_token,
                signer_token=signer.token
            )
        except (ZapSignAuthenticationError, ZapSignValidationError, ZapSignAPIError) as e:
            # Re-raise ZapSign-specific errors as they contain useful information
            raise e

        # Update signer with latest data from ZapSign
        updated_signer = self._update_signer_with_zapsign_data(signer, zapsign_signer_data)

        # Save the updated signer
        saved_signer = self._signer_repository.save(updated_signer)

        return SyncSignerWithZapSignOutput(
            signer=saved_signer,
            success=True
        )

    def _update_signer_with_zapsign_data(
        self,
        signer: Signer,
        zapsign_data: ZapSignSignerResponse
    ) -> Signer:
        """Update signer entity with data from ZapSign."""
        # Parse datetime strings from ZapSign response
        last_view_at = None
        if zapsign_data.last_view_at:
            try:
                last_view_at = datetime.fromisoformat(zapsign_data.last_view_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # If parsing fails, keep the existing value
                last_view_at = signer.last_view_at

        signed_at = None
        if zapsign_data.signed_at:
            try:
                signed_at = datetime.fromisoformat(zapsign_data.signed_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # If parsing fails, keep the existing value
                signed_at = signer.signed_at

        # Create updated signer with ZapSign data
        return Signer(
            id=signer.id,
            name=signer.name,
            email=signer.email,
            token=signer.token,
            status=zapsign_data.status,
            external_id=signer.external_id,
            sign_url=signer.sign_url,
            company_id=signer.company_id,
            created_at=signer.created_at,
            last_updated_at=datetime.now(),  # Update timestamp
            document_ids=signer.document_ids,
            # ZapSign sync fields
            times_viewed=zapsign_data.times_viewed,
            last_view_at=last_view_at,
            signed_at=signed_at,
        )