from dataclasses import asdict

from core.entities.company import Company
from core.interfaces.dtos import CreateCompanyDTO, CompanyDTO
from core.interfaces.repositories import ICompanyRepository


class CreateCompanyUseCase:
    def __init__(self, company_repo: ICompanyRepository) -> None:
        self._company_repo = company_repo

    def execute(self, data: CreateCompanyDTO) -> CompanyDTO:
        # Basic entity-level validation happens on Company
        Company(id=None, name=data.name, api_token=data.api_token)
        return self._company_repo.create(data)

