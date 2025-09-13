from __future__ import annotations

from core.repositories import CompanyRepository as DjangoCompanyRepository
from core.repositories.contracts import CompanyRepositoryProtocol
from core.use_cases.company.create_company import CreateCompanyUseCase
from core.use_cases.company.list_companies import ListCompaniesUseCase
from core.use_cases.company.get_company import GetCompanyUseCase
from core.use_cases.company.delete_company import DeleteCompanyUseCase


def get_company_repository() -> CompanyRepositoryProtocol:
    return DjangoCompanyRepository()


def get_create_company_use_case() -> CreateCompanyUseCase:
    return CreateCompanyUseCase(get_company_repository())


def get_list_companies_use_case() -> ListCompaniesUseCase:
    return ListCompaniesUseCase(get_company_repository())


def get_get_company_use_case() -> GetCompanyUseCase:
    return GetCompanyUseCase(get_company_repository())


def get_delete_company_use_case() -> DeleteCompanyUseCase:
    return DeleteCompanyUseCase(get_company_repository())
