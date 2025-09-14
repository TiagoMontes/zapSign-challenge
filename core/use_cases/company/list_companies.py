from core.domain.entities.company import Company
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


class ListCompanies:
    """Use case for listing all companies."""

    def __init__(self, repository: CompanyRepositoryProtocol):
        self._repository = repository

    def execute(self) -> list[Company]:
        """Execute the list companies use case."""
        return self._repository.find_all()
