from django.test import TestCase
from core.domain.entities.company import Company
from core.use_cases.company.delete_company import DeleteCompany, DeleteCompanyInput
from core.use_cases.company.exceptions import CompanyNotFoundError
from tests.fakes.company_repo import FakeCompanyRepository


class TestDeleteCompanyUseCase(TestCase):
    """Test Delete Company use case."""

    def setUp(self):
        """Set up test data."""
        self.repository = FakeCompanyRepository()
        self.use_case = DeleteCompany(self.repository)

    def test_execute_should_delete_company_when_exists(self):
        """Test that execute deletes company when it exists."""
        # Create company first
        company = Company(id=1, name="Test Company", api_token="test-token")
        self.repository.save(company)

        input_data = DeleteCompanyInput(company_id=1)
        self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        # Verify company is deleted from repository
        deleted_company = self.repository.find_by_id(1)
        self.assertIsNone(deleted_company)

    def test_execute_should_raise_error_when_company_not_found(self):
        """Test that execute raises error when company is not found."""
        input_data = DeleteCompanyInput(company_id=999)

        with self.assertRaises(CompanyNotFoundError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company with ID 999 not found", str(cm.exception))