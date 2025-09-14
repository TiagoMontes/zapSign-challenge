from dataclasses import dataclass
from datetime import datetime, timezone
from django.db import transaction
from core.domain.entities.company import Company
from core.repositories.company_repository_protocol import CompanyRepositoryProtocol


@dataclass
class CreateCompanyInput:
    """Input data for creating a company."""
    name: str
    api_token: str


class CreateCompany:
    """Use case for creating a new company."""

    def __init__(self, repository: CompanyRepositoryProtocol):
        self._repository = repository

    @transaction.atomic
    def execute(self, input_data: CreateCompanyInput) -> Company:  # type: ignore[reportArgumentType]
        """Execute the create company use case."""
        # Check if company name already exists
        if self._repository.exists_by_name(input_data.name):
            raise ValueError(f"Company with name '{input_data.name}' already exists")

        # Create company entity with current timestamp
        now = datetime.now(timezone.utc)
        company = Company(
            name=input_data.name,
            api_token=input_data.api_token,
            created_at=now,
            last_updated_at=now
        )

        # Validate company entity
        if not company.is_valid():
            errors = company.get_validation_errors()
            error_messages = list(errors.values())
            raise ValueError(f"Invalid company data: {', '.join(error_messages)}")

        # Save company
        return self._repository.save(company)
