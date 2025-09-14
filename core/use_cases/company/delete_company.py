from dataclasses import dataclass
from django.db import transaction
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


@dataclass
class DeleteCompanyInput:
    """Input data for deleting a company."""
    company_id: int


class DeleteCompany:
    """Use case for deleting a company by ID."""

    def __init__(self, repository: CompanyRepositoryProtocol):
        self._repository = repository

    @transaction.atomic
    def execute(self, input_data: DeleteCompanyInput) -> None:
        """Execute the delete company use case."""
        # Check if company exists
        if not self._repository.exists_by_id(input_data.company_id):
            raise ValueError(f"Company with ID {input_data.company_id} not found")

        # Delete company
        self._repository.delete_by_id(input_data.company_id)
