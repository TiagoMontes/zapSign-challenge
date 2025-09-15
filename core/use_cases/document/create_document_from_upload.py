"""Use case for creating a document from ZapSign upload."""

from dataclasses import dataclass
from typing import List, Protocol

from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.domain.entities.signer import Signer
from core.domain.value_objects.zapsign_request import ZapSignDocumentRequest
from core.domain.value_objects.zapsign_response import (
    ZapSignDocumentResponse,
    ZapSignSignerResponse,
)
from core.services.zapsign_service import ZapSignService
from core.repositories.contracts import DocumentRepository, SignerRepository


@dataclass
class CreateDocumentFromUploadResult:
    """Result of document creation from upload."""

    document: Document
    signers: List[Signer]
    zapsign_response: ZapSignDocumentResponse


class CreateDocumentFromUploadUseCase:
    """Use case for creating documents via ZapSign API."""

    def __init__(
        self,
        zapsign_service: ZapSignService,
        document_repository: DocumentRepository,
        signer_repository: SignerRepository,
    ):
        self.zapsign_service = zapsign_service
        self.document_repository = document_repository
        self.signer_repository = signer_repository

    def execute(
        self, company: Company, request: ZapSignDocumentRequest
    ) -> CreateDocumentFromUploadResult:
        """
        Create a document via ZapSign API and save to database.

        Args:
            company: The company creating the document
            request: The document creation request

        Returns:
            CreateDocumentFromUploadResult with created document and signers

        Raises:
            ZapSignAPIError: If API call fails
        """
        # 1. Call ZapSign API using company's token
        zapsign_response = self.zapsign_service.create_document(
            api_token=company.api_token, request=request
        )

        # 2. Create Document entity from response
        document = Document(
            id=None,  # Will be set by repository
            company_id=company.id,
            name=zapsign_response.name,
            token=zapsign_response.token,
            open_id=zapsign_response.open_id,
            status=zapsign_response.status,
            external_id=zapsign_response.external_id,
            created_by=zapsign_response.created_by_email,
        )

        # 3. Save document to database
        saved_document = self.document_repository.save(document)

        # 4. Create and save signers if any
        signers = []
        if zapsign_response.signers:
            # Create Signer entities from response
            for signer_response in zapsign_response.signers:
                signer = Signer(
                    id=None,  # Will be set by repository
                    name=signer_response.name,
                    email=signer_response.email,
                    token=signer_response.token,
                    status=signer_response.status,
                    external_id=signer_response.external_id,
                )
                signers.append(signer)

            # Bulk save signers
            saved_signers = self.signer_repository.save_bulk(signers)

            # 5. Associate signers with document
            if saved_document.id is not None:
                signer_ids = [s.id for s in saved_signers if s.id is not None]
                self.document_repository.add_signers(
                    document_id=saved_document.id, signer_ids=signer_ids
                )

            signers = saved_signers

        # 6. Return result
        return CreateDocumentFromUploadResult(
            document=saved_document,
            signers=signers,
            zapsign_response=zapsign_response,
        )