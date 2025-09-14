from dataclasses import dataclass
from datetime import datetime, timezone
from django.db import transaction
from core.domain.entities.company import Company
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


@dataclass
class UpdateCompanyInput:
    """Input data for updating a company."""
    company_id: int
    name: str
    api_token: str


class UpdateCompany:
    """Use case for updating an existing company."""

    def __init__(self, repository: CompanyRepositoryProtocol):
        self._repository = repository

    @transaction.atomic
    def execute(self, input_data: UpdateCompanyInput) -> Company:  # type: ignore[reportArgumentType]
        """Execute the update company use case."""
        # Find existing company
        existing_company = self._repository.find_by_id(input_data.company_id)
        if existing_company is None:
            raise ValueError(f"Company with ID {input_data.company_id} not found")

        # Check if the new name conflicts with another company (only if name is being changed)
        if input_data.name != existing_company.name and self._repository.exists_by_name(input_data.name):
            raise ValueError(f"Company with name '{input_data.name}' already exists")

        # Create updated company entity
        updated_company = Company(
            id=input_data.company_id,
            name=input_data.name,
            api_token=input_data.api_token,
            created_at=existing_company.created_at,
            last_updated_at=datetime.now(timezone.utc)
        )

        # Validate company entity
        if not updated_company.is_valid():
            errors = updated_company.get_validation_errors()
            error_messages = list(errors.values())
            raise ValueError(f"Invalid company data: {', '.join(error_messages)}")

        # Save updated company
        return self._repository.save(updated_company)