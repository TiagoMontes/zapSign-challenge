from typing import Iterable

from core.domain.entities.company import Company
from core.repositories.contracts import CompanyRepositoryProtocol


class ListCompaniesUseCase:
    def __init__(self, company_repo: CompanyRepositoryProtocol) -> None:
        self._company_repo = company_repo

    def execute(self) -> Iterable[Company]:
        return self._company_repo.list()