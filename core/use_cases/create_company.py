from core.domain.entities.company import Company
from core.repositories.company_repo import CompanyRepository


class CreateCompanyUseCase:
    def __init__(self, company_repo: CompanyRepository) -> None:
        self._company_repo = company_repo

    def execute(self, company: Company) -> Company:
        # Basic entity-level validation happens on Company
        _ = Company(id=None, name=company.name, api_token=company.api_token)
        return self._company_repo.create(company)
