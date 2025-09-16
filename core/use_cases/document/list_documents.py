"""List documents use case."""

from dataclasses import dataclass
from typing import List, Optional, Protocol
from core.domain.entities.document import Document
from core.domain.entities.company import Company


class DocumentRepositoryProtocol(Protocol):
    """Protocol for document repository."""

    def find_by_company(self, company_id: int, include_deleted: bool = False) -> List[Document]:
        """Find all documents belonging to a specific company."""
        ...


@dataclass
class ListDocumentsInput:
    """Input data for listing documents."""
    company: Company
    include_deleted: bool = False
    page: int = 1
    page_size: int = 10


@dataclass
class ListDocumentsOutput:
    """Output data for listing documents."""
    documents: List[Document]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class ListDocumentsUseCase:
    """Use case for listing documents with company filtering and pagination."""

    def __init__(self, document_repository: DocumentRepositoryProtocol) -> None:
        self._document_repository = document_repository

    def execute(self, input_data: ListDocumentsInput) -> ListDocumentsOutput:
        """Execute the list documents use case."""
        # Get all documents for the company
        all_documents = self._document_repository.find_by_company(
            company_id=input_data.company.id,
            include_deleted=input_data.include_deleted
        )

        total_count = len(all_documents)

        # Calculate pagination
        start_index = (input_data.page - 1) * input_data.page_size
        end_index = start_index + input_data.page_size
        paginated_documents = all_documents[start_index:end_index]

        # Calculate pagination metadata
        has_previous = input_data.page > 1
        has_next = end_index < total_count

        return ListDocumentsOutput(
            documents=paginated_documents,
            total_count=total_count,
            page=input_data.page,
            page_size=input_data.page_size,
            has_next=has_next,
            has_previous=has_previous,
        )