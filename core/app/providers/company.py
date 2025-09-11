from __future__ import annotations

from core.repositories import CompanyRepository
from core.use_cases.create_company import CreateCompanyUseCase


def get_company_repository() -> CompanyRepository:
    return CompanyRepository()


def get_create_company_use_case() -> CreateCompanyUseCase:
    return CreateCompanyUseCase(get_company_repository())
