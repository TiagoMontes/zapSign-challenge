from django.test import TestCase
from core.domain.entities.company import Company
from core.use_cases.company.get_company import GetCompany, GetCompanyInput
from core.use_cases.company.exceptions import CompanyNotFoundError
from tests.fakes.company_repo import FakeCompanyRepository


class TestGetCompanyUseCase(TestCase):
    """Test Get Company use case."""

    def setUp(self):
        """Set up test data."""
        self.repository = FakeCompanyRepository()
        self.use_case = GetCompany(self.repository)

    def test_execute_should_return_company_when_exists(self):
        """Test that execute returns company when it exists."""
        # Create company
        company = Company(id=1, name="Test Company", api_token="test-token")
        self.repository.save(company)

        input_data = GetCompanyInput(company_id=1)
        result = self.use_case.execute(input_data)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "test-token")

    def test_execute_should_raise_error_when_company_not_found(self):
        """Test that execute raises error when company is not found."""
        input_data = GetCompanyInput(company_id=999)

        with self.assertRaises(CompanyNotFoundError) as cm:
            self.use_case.execute(input_data)

        self.assertIn("Company with ID 999 not found", str(cm.exception))