from django.test import SimpleTestCase

from core.domain.entities.company import Company
from tests.fakes.company_repo import InMemoryCompanyRepository
from core.use_cases.create_company import CreateCompanyUseCase


class CreateCompanyUseCaseTests(SimpleTestCase):
    def test_create_company_use_case_creates_company(self):
        repo = InMemoryCompanyRepository()
        uc = CreateCompanyUseCase(repo)
        result = uc.execute(Company(name="Acme"))
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Acme")

