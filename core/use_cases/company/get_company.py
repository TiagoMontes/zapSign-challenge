from dataclasses import dataclass
from core.domain.entities.company import Company
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


@dataclass
class GetCompanyInput:
    """Input data for getting a company."""
    company_id: int


class GetCompany:
    """Use case for getting a company by ID."""

    def __init__(self, repository: CompanyRepositoryProtocol):
        self._repository = repository

    def execute(self, input_data: GetCompanyInput) -> Company:
        """Execute the get company use case."""
        company = self._repository.find_by_id(input_data.company_id)

        if company is None:
            raise ValueError(f"Company with ID {input_data.company_id} not found")

        return company
