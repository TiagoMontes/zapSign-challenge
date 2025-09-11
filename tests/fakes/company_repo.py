from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.company import Company


class InMemoryCompanyRepository:
    def __init__(self) -> None:
        self._seq = 0
        self._items: dict[int, Company] = {}

    def create(self, company: Company) -> Company:
        self._seq += 1
        c = Company(id=self._seq, name=company.name, api_token=company.api_token)
        self._items[self._seq] = c
        return c

    def get_by_id(self, company_id: int) -> Optional[Company]:
        return self._items.get(company_id)

    def list(self) -> Iterable[Company]:
        return list(self._items.values())

    def delete(self, company_id: int) -> None:
        self._items.pop(company_id, None)

