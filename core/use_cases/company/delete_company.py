from __future__ import annotations

from django.db import transaction

from core.repositories.contracts import CompanyRepositoryProtocol


class DeleteCompanyUseCase:
    def __init__(self, company_repo: CompanyRepositoryProtocol) -> None:
        self._company_repo = company_repo

    def execute(self, company_id: int) -> None:
        with transaction.atomic():  # type: ignore[attr-defined]
            self._company_repo.delete(company_id)