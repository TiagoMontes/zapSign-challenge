"""Update signer in ZapSign use case."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, Protocol
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

    def update_signer(self, api_token: str, signer_token: str, data: Dict[str, Any]) -> ZapSignSignerResponse:
        """Update a signer in ZapSign API."""
        ...


@dataclass
class UpdateSignerInZapSignInput:
    """Input data for updating a signer in ZapSign."""
    signer_id: int
    update_data: Dict[str, Any]


@dataclass
class UpdateSignerInZapSignOutput:
    """Output data for updating a signer in ZapSign."""
    signer: Signer
    success: bool


class SignerNotFoundError(Exception):
    """Exception raised when signer is not found."""
    pass


class SignerUpdateError(Exception):
    """Exception raised when signer cannot be updated."""
    pass


class CompanyNotFoundError(Exception):
    """Exception raised when company is not found."""
    pass


class UpdateSignerInZapSignUseCase:
    """Use case for updating a signer in ZapSign."""

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
    def execute(self, input_data: UpdateSignerInZapSignInput) -> UpdateSignerInZapSignOutput:
        """Execute the update signer in ZapSign use case."""
        # Find signer by ID
        signer = self._signer_repository.find_by_id(input_data.signer_id)

        if signer is None:
            raise SignerNotFoundError("Signer not found")

        # Check if signer has a token for ZapSign update
        if not signer.token:
            raise SignerUpdateError("Signer has no token for ZapSign update")

        # Get company information to retrieve API token
        if signer.company_id is None:
            raise CompanyNotFoundError("Signer has no associated company")

        company = self._company_repository.find_by_id(signer.company_id)
        if company is None:
            raise CompanyNotFoundError("Associated company not found")

        # Update signer in ZapSign first
        try:
            zapsign_signer_data = self._zapsign_service.update_signer(
                api_token=company.api_token,
                signer_token=signer.token,
                data=input_data.update_data
            )
        except (ZapSignAuthenticationError, ZapSignValidationError, ZapSignAPIError) as e:
            # Re-raise ZapSign-specific errors as they contain useful information
            raise e

        # Update signer with latest data from ZapSign and local updates
        updated_signer = self._update_signer_with_zapsign_data(signer, zapsign_signer_data, input_data.update_data)

        # Save the updated signer
        saved_signer = self._signer_repository.save(updated_signer)

        return UpdateSignerInZapSignOutput(
            signer=saved_signer,
            success=True
        )

    def _update_signer_with_zapsign_data(
        self,
        signer: Signer,
        zapsign_data: ZapSignSignerResponse,
        local_updates: Dict[str, Any]
    ) -> Signer:
        """Update signer entity with data from ZapSign and local updates."""
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

        # Apply local updates first, then ZapSign data takes precedence for sync fields
        updated_name = local_updates.get('name', signer.name)
        updated_email = local_updates.get('email', signer.email)

        # Create updated signer with combined data
        return Signer(
            id=signer.id,
            name=updated_name,
            email=updated_email,
            token=signer.token,
            status=zapsign_data.status,  # ZapSign is source of truth for status
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