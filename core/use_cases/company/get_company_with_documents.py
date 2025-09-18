from dataclasses import dataclass
from typing import List
from core.domain.entities.company import Company
from core.domain.entities.document import Document
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol
from core.repositories.document_repository_protocol import DocumentRepositoryProtocol
from .exceptions import CompanyNotFoundError


@dataclass
class GetCompanyWithDocumentsInput:
    """Input data for getting a company with its documents."""
    company_id: int


@dataclass
class CompanyWithDocuments:
    """Data structure representing a company with its associated documents."""
    id: int
    name: str
    api_token: str
    created_at: str
    last_updated_at: str
    documents: List[Document]

    @classmethod
    def from_company(cls, company: Company, documents: List[Document]) -> 'CompanyWithDocuments':
        """Create CompanyWithDocuments from a Company entity and documents list."""
        return cls(
            id=company.id or 0,
            name=company.name,
            api_token=company.api_token,
            created_at=company.created_at.isoformat() if company.created_at else "",
            last_updated_at=company.last_updated_at.isoformat() if company.last_updated_at else "",
            documents=documents
        )


class GetCompanyWithDocuments:
    """Use case for getting a company by ID along with its documents."""

    def __init__(self, company_repository: CompanyRepositoryProtocol, document_repository: DocumentRepositoryProtocol):
        self._company_repository = company_repository
        self._document_repository = document_repository

    def execute(self, input_data: GetCompanyWithDocumentsInput) -> CompanyWithDocuments:
        """Execute the get company with documents use case."""
        # Get the company
        company = self._company_repository.find_by_id(input_data.company_id)

        if company is None:
            raise CompanyNotFoundError(f"Company with ID {input_data.company_id} not found")

        # Get the company's documents
        documents = self._document_repository.find_by_company(input_data.company_id, include_deleted=False)

        # Return the combined result
        return CompanyWithDocuments.from_company(company, documents)