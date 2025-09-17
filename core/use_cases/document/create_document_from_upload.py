"""Use case for creating a document from ZapSign upload."""

import uuid
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
from core.services.pdf.pdf_service import PDFService
from core.services.pdf.interfaces import PDFProcessingError
from core.repositories.contracts import DocumentRepository, SignerRepository


@dataclass
class CreateDocumentFromUploadResult:
    """Result of document creation from upload."""

    document: Document
    signers: List[Signer]
    zapsign_response: ZapSignDocumentResponse


class CreateDocumentFromUploadUseCase:
    """Use case for creating documents via ZapSign API with PDF processing."""

    def __init__(
        self,
        zapsign_service: ZapSignService,
        document_repository: DocumentRepository,
        signer_repository: SignerRepository,
        pdf_service: PDFService,
    ):
        self.zapsign_service = zapsign_service
        self.document_repository = document_repository
        self.signer_repository = signer_repository
        self.pdf_service = pdf_service

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

        # 2. Create Document entity from response with PDF processing fields
        document = Document(
            id=None,  # Will be set by repository
            company_id=company.id,
            name=zapsign_response.name,
            token=zapsign_response.token,
            open_id=zapsign_response.open_id,
            status=zapsign_response.status,
            external_id=zapsign_response.external_id,
            created_by=zapsign_response.created_by_email,
            url_pdf=request.url_pdf,  # Store PDF URL
            processing_status="UPLOADED",  # Initial status
            version_id=str(uuid.uuid4()),  # Generate unique version ID
        )

        # 3. Save document to database first
        saved_document = self.document_repository.save(document)

        # 4. Process PDF if URL provided (async in future, sync for now)
        if request.url_pdf and saved_document.id:
            self._process_pdf_document(saved_document, request.url_pdf)

        # 5. Create and save signers if any
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
                    sign_url=signer_response.sign_url,
                )
                signers.append(signer)

            # Bulk save signers
            saved_signers = self.signer_repository.save_bulk(signers)

            # 6. Associate signers with document
            if saved_document.id is not None:
                signer_ids = [s.id for s in saved_signers if s.id is not None]
                self.document_repository.add_signers(
                    document_id=saved_document.id, signer_ids=signer_ids
                )

            signers = saved_signers

            # Update document entity with signers for serialization
            saved_document.signers = saved_signers

        # 7. Return result
        return CreateDocumentFromUploadResult(
            document=saved_document,
            signers=signers,
            zapsign_response=zapsign_response,
        )

    def _process_pdf_document(self, document: Document, url_pdf: str) -> None:
        """Process PDF document: download, extract text, and index.

        Args:
            document: Document entity to process
            url_pdf: URL of the PDF to process
        """
        try:
            print(f"[DEBUG] Starting PDF processing for document {document.id} from {url_pdf}")

            # Update status to PROCESSING
            document.processing_status = "PROCESSING"
            self.document_repository.save(document)

            # Download and extract text from PDF
            text_content, checksum = self.pdf_service.download_and_extract_text(url_pdf)

            # Create chunks and embeddings for AI analysis
            self._create_embeddings_for_document(document, text_content)

            # Update document with processing results
            document.checksum = checksum
            document.processing_status = "INDEXED"
            self.document_repository.save(document)

            print(f"[DEBUG] PDF processing completed for document {document.id}. "
                  f"Extracted {len(text_content)} characters, checksum: {checksum[:8]}...")

        except PDFProcessingError as e:
            print(f"[ERROR] PDF processing failed for document {document.id}: {e}")
            # Update status to FAILED
            document.processing_status = "FAILED"
            self.document_repository.save(document)
            # Don't raise exception - document creation should still succeed
        except Exception as e:
            print(f"[ERROR] Unexpected error processing PDF for document {document.id}: {e}")
            document.processing_status = "FAILED"
            self.document_repository.save(document)

    def _create_embeddings_for_document(self, document: Document, text_content: str) -> None:
        """Create embeddings and store in ChromaDB for AI analysis.

        Args:
            document: Document entity
            text_content: Extracted text from PDF
        """
        try:
            from core.services.analysis.ai_service import AIAnalysisService
            from langchain.schema import Document as LangChainDocument

            print(f"[DEBUG] Creating embeddings for document {document.id} with {len(text_content)} characters")

            # Initialize AI service for chunking and embedding
            ai_service = AIAnalysisService()

            # Create chunks using the same text splitter as AI service
            text_chunks = ai_service.text_splitter.split_text(text_content)
            print(f"[DEBUG] Created {len(text_chunks)} chunks for document {document.id}")

            # Create LangChain documents with metadata (only non-None values)
            docs = []
            for i, chunk in enumerate(text_chunks):
                metadata = {
                    "document_id": document.id,
                    "document_name": document.name,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "status": document.status or "unknown",
                }

                # Only add non-None values to metadata
                if document.url_pdf:
                    metadata["url_pdf"] = document.url_pdf
                if document.checksum:
                    metadata["checksum"] = document.checksum

                doc = LangChainDocument(
                    page_content=chunk,
                    metadata=metadata
                )
                docs.append(doc)

            # Add to ChromaDB
            ai_service.vectorstore.add_documents(docs)
            print(f"[DEBUG] Successfully added {len(docs)} chunks to ChromaDB for document {document.id}")

        except Exception as e:
            print(f"[ERROR] Failed to create embeddings for document {document.id}: {e}")
            # Don't raise - let document creation continue