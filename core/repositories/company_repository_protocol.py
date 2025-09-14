from typing import Protocol, Optional
from core.domain.entities.company import Company


class CompanyRepositoryProtocol(Protocol):
    """Protocol defining the interface for Company repositories."""

    def save(self, company: Company) -> Company:
        """Save a company entity."""
        ...

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        ...

    def find_all(self) -> list[Company]:
        """Find all companies ordered by ID descending."""
        ...

    def delete_by_id(self, company_id: int) -> bool:
        """Delete a company by its ID."""
        ...

    def exists_by_id(self, company_id: int) -> bool:
        """Check if a company exists by its ID."""
        ...

    def exists_by_name(self, name: str) -> bool:
        """Check if a company exists by its name."""
        ...