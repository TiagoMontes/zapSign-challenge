from typing import Optional
from core.domain.entities.company import Company
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


class FakeCompanyRepository(CompanyRepositoryProtocol):
    """Fake Company repository for testing use cases."""

    def __init__(self):
        self._companies: dict[int, Company] = {}
        self._next_id = 1

    def save(self, company: Company) -> Company:
        """Save a company entity."""
        if company.id is None:
            # Create new company
            new_id = self._next_id
            self._next_id += 1
            saved_company = Company(
                id=new_id,
                name=company.name,
                api_token=company.api_token,
                created_at=company.created_at,
                last_updated_at=company.last_updated_at
            )
            self._companies[new_id] = saved_company
            return saved_company
        else:
            # Update existing company
            self._companies[company.id] = company
            return company

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        return self._companies.get(company_id)

    def find_all(self) -> list[Company]:
        """Find all companies ordered by ID descending."""
        companies = list(self._companies.values())
        return sorted(companies, key=lambda c: c.id or 0, reverse=True)

    def delete_by_id(self, company_id: int) -> bool:
        """Delete a company by its ID."""
        if company_id in self._companies:
            del self._companies[company_id]
            return True
        return False

    def exists_by_id(self, company_id: int) -> bool:
        """Check if a company exists by its ID."""
        return company_id in self._companies

    def exists_by_name(self, name: str) -> bool:
        """Check if a company exists by its name."""
        return any(company.name == name for company in self._companies.values())
