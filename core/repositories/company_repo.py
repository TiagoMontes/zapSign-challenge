from typing import Optional
from django.db import transaction
from core.domain.entities.company import Company
from core.orm.models import Company as CompanyModel
from core.orm.mappers import company_model_to_entity, company_entity_to_model_data


class CompanyRepository:
    """Repository for Company entity using Django ORM."""

    def save(self, company: Company) -> Company:
        """Save a company entity to the database."""
        with transaction.atomic():  # type: ignore[reportGeneralTypeIssues]
            if company.id:
                # Update existing company
                company_model = CompanyModel.objects.get(id=company.id)
                model_data = company_entity_to_model_data(company)
                for key, value in model_data.items():
                    setattr(company_model, key, value)
                company_model.save()  # This will update last_updated_at automatically
            else:
                # Create new company
                model_data = company_entity_to_model_data(company)
                company_model = CompanyModel.objects.create(**model_data)

            return company_model_to_entity(company_model)

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find a company by its ID."""
        try:
            company_model = CompanyModel.objects.get(id=company_id)
            return company_model_to_entity(company_model)
        except CompanyModel.DoesNotExist:  # type: ignore[reportAttributeAccessIssue]
            return None

    def find_all(self) -> list[Company]:
        """Find all companies ordered by ID descending."""
        company_models = CompanyModel.objects.all().order_by("-id")
        return [company_model_to_entity(model) for model in company_models]

    def delete_by_id(self, company_id: int) -> bool:
        """Delete a company by its ID."""
        deleted_count, _ = CompanyModel.objects.filter(id=company_id).delete()
        return deleted_count > 0

    def exists_by_id(self, company_id: int) -> bool:
        """Check if a company exists by its ID."""
        return CompanyModel.objects.filter(id=company_id).exists()

    def exists_by_name(self, name: str) -> bool:
        """Check if a company exists by its name."""
        return CompanyModel.objects.filter(name=name).exists()
