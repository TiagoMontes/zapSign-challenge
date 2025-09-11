from django.test import SimpleTestCase

from core.interfaces.dtos import CreateCompanyDTO, CompanyDTO
from core.interfaces.repositories import ICompanyRepository
from core.use_cases.create_company import CreateCompanyUseCase


class InMemoryCompanyRepo(ICompanyRepository):
    def __init__(self) -> None:
        self._data: list[CompanyDTO] = []
        self._seq = 0

    def create(self, data: CreateCompanyDTO) -> CompanyDTO:
        self._seq += 1
        dto = CompanyDTO(id=self._seq, name=data.name, api_token=data.api_token)
        self._data.append(dto)
        return dto

    def get_by_id(self, company_id: int):
        return next((c for c in self._data if c.id == company_id), None)

    def list(self):
        return list(self._data)

    def delete(self, company_id: int) -> None:
        self._data = [c for c in self._data if c.id != company_id]


class CreateCompanyUseCaseTests(SimpleTestCase):
    def test_create_company_use_case_creates_company(self):
        repo = InMemoryCompanyRepo()
        uc = CreateCompanyUseCase(repo)
        result = uc.execute(CreateCompanyDTO(name="Acme"))
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Acme")
