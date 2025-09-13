from typing import Optional

from core.domain.entities.company import Company
from core.repositories.contracts import CompanyRepositoryProtocol


class GetCompanyUseCase:
    def __init__(self, company_repo: CompanyRepositoryProtocol) -> None:
        self._company_repo = company_repo

    def execute(self, company_id: int) -> Optional[Company]:
        return self._company_repo.get_by_id(company_id)