from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.company import Company as CompanyEntity
from core.orm.models import Company as CompanyModel
from core.orm.mappers import (
    company_model_to_entity,
    company_entity_to_model_data,
    map_companies,
)


class CompanyRepository:
    def create(self, company: CompanyEntity) -> CompanyEntity:
        obj = CompanyModel.objects.create(**company_entity_to_model_data(company))
        return company_model_to_entity(obj)

    def get_by_id(self, company_id: int) -> Optional[CompanyEntity]:
        obj = CompanyModel.objects.filter(id=company_id).first()
        return company_model_to_entity(obj) if obj else None

    def list(self) -> Iterable[CompanyEntity]:
        return map_companies(CompanyModel.objects.order_by("-id").all())

    def delete(self, company_id: int) -> None:
        CompanyModel.objects.filter(id=company_id).delete()

