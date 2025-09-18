"""Add signer to document use case."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, Protocol
from django.db import transaction

from core.domain.entities.signer import Signer
from core.domain.entities.document import Document
from core.domain.entities.company import Company
from core.domain.value_objects.zapsign_response import ZapSignSignerResponse
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class DocumentRepositoryProtocol(Protocol):
    """Protocol for document repository."""

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find a document by ID."""
        ...

    def add_signers(self, document_id: int, signer_ids: list[int]) -> None:
        """Associate signers with a document."""
        ...


class SignerRepositoryProtocol(Protocol):
    """Protocol for signer repository."""

    def save(self, signer: Signer) -> Signer:
        """Save a signer and return it with ID."""
        ...

    def find_by_id(self, signer_id: int) -> Optional[Signer]:
        """Find a signer by ID."""
        ...


class CompanyRepositoryProtocol(Protocol):
    """Protocol for company repository."""

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        ...


class ZapSignServiceProtocol(Protocol):
    """Protocol for ZapSign service."""

    def add_signer_to_document(self, api_token: str, doc_token: str, signer_data: Dict[str, Any]) -> ZapSignSignerResponse:
        """Add a new signer to an existing document in ZapSign API."""
        ...


@dataclass
class AddSignerToDocumentInput:
    """Input data for adding a signer to a document."""
    document_id: int
    signer_data: Dict[str, Any]


@dataclass
class AddSignerToDocumentOutput:
    """Output data for adding a signer to a document."""
    signer: Signer
    success: bool


class DocumentNotFoundError(Exception):
    """Exception raised when document is not found."""
    pass


class DocumentAddSignerError(Exception):
    """Exception raised when signer cannot be added to document."""
    pass


class CompanyNotFoundError(Exception):
    """Exception raised when company is not found."""
    pass


class AddSignerToDocumentUseCase:
    """Use case for adding a signer to a document via ZapSign."""

    def __init__(
        self,
        document_repository: DocumentRepositoryProtocol,
        signer_repository: SignerRepositoryProtocol,
        company_repository: CompanyRepositoryProtocol,
        zapsign_service: ZapSignServiceProtocol
    ) -> None:
        self._document_repository = document_repository
        self._signer_repository = signer_repository
        self._company_repository = company_repository
        self._zapsign_service = zapsign_service

    @transaction.atomic
    def execute(self, input_data: AddSignerToDocumentInput) -> AddSignerToDocumentOutput:
        """Execute the add signer to document use case."""
        # Find document by ID
        document = self._document_repository.find_by_id(input_data.document_id)

        if document is None:
            raise DocumentNotFoundError("Document not found")

        # Check if document has a token for ZapSign integration
        if not document.token:
            raise DocumentAddSignerError("Document has no token for ZapSign integration")

        # Get company information to retrieve API token
        if document.company_id is None:
            raise CompanyNotFoundError("Document has no associated company")

        company = self._company_repository.find_by_id(document.company_id)
        if company is None:
            raise CompanyNotFoundError("Associated company not found")

        # Add signer to document in ZapSign
        try:
            zapsign_signer_data = self._zapsign_service.add_signer_to_document(
                api_token=company.api_token,
                doc_token=document.token,
                signer_data=input_data.signer_data
            )
        except (ZapSignAuthenticationError, ZapSignValidationError, ZapSignAPIError) as e:
            # Re-raise ZapSign-specific errors as they contain useful information
            raise e

        # Create new signer entity from ZapSign response and local data
        new_signer = self._create_signer_from_zapsign_data(
            zapsign_data=zapsign_signer_data,
            local_data=input_data.signer_data,
            company_id=document.company_id,
            document_id=document.id
        )

        # Save the new signer
        saved_signer = self._signer_repository.save(new_signer)

        # Associate the signer with the document (M2M relationship)
        if saved_signer.id is not None and document.id is not None:
            self._document_repository.add_signers(document.id, [saved_signer.id])

            # Re-fetch the signer to get the updated associations
            refreshed_signer = self._signer_repository.find_by_id(saved_signer.id)
            if refreshed_signer is not None:
                saved_signer = refreshed_signer

        return AddSignerToDocumentOutput(
            signer=saved_signer,
            success=True
        )

    def _create_signer_from_zapsign_data(
        self,
        zapsign_data: ZapSignSignerResponse,
        local_data: Dict[str, Any],
        company_id: int,
        document_id: Optional[int]
    ) -> Signer:
        """Create signer entity from ZapSign response and local data."""
        # Parse datetime strings from ZapSign response
        last_view_at = None
        if zapsign_data.last_view_at:
            try:
                last_view_at = datetime.fromisoformat(zapsign_data.last_view_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                last_view_at = None

        signed_at = None
        if zapsign_data.signed_at:
            try:
                signed_at = datetime.fromisoformat(zapsign_data.signed_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                signed_at = None

        # Use local data for name and email, fallback to ZapSign data
        name = local_data.get('name', zapsign_data.name)
        email = local_data.get('email', zapsign_data.email)

        # Build document_ids list
        document_ids = [document_id] if document_id else []

        # Create new signer entity
        return Signer(
            id=None,  # Will be assigned by repository
            name=name,
            email=email,
            token=zapsign_data.token,
            status=zapsign_data.status,
            external_id=zapsign_data.external_id,
            sign_url=zapsign_data.sign_url,
            company_id=company_id,
            created_at=datetime.now(),
            last_updated_at=datetime.now(),
            document_ids=document_ids,
            # ZapSign sync fields
            times_viewed=zapsign_data.times_viewed,
            last_view_at=last_view_at,
            signed_at=signed_at,
        )