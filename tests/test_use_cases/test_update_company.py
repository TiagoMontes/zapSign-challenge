from django.test import TestCase
from core.domain.entities.company import Company
from core.use_cases.company.update_company import UpdateCompany, UpdateCompanyInput
from core.use_cases.company.exceptions import CompanyNotFoundError, CompanyAlreadyExistsError, CompanyValidationError
from tests.fakes.company_repo import FakeCompanyRepository


class TestUpdateCompanyUseCase(TestCase):
    """Test Update Company use case."""

    def setUp(self):
        """Set up test data."""
        self.repository = FakeCompanyRepository()
        self.use_case = UpdateCompany(self.repository)

    def test_execute_should_update_company_when_valid_input_provided(self):
        """Test that execute updates company when valid input is provided."""
        # Create company first
        company = Company(id=1, name="Original Name", api_token="original-token")
        self.repository.save(company)

        input_data = UpdateCompanyInput(
            company_id=1,
            name="Updated Name",
            api_token="updated-token"
        )

        result = self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        # Type narrowing to help Pyright understand the return type
        assert isinstance(result, Company)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Updated Name")
        self.assertEqual(result.api_token, "updated-token")

        # Verify company is updated in repository
        updated_company = self.repository.find_by_id(1)
        self.assertIsNotNone(updated_company)
        assert updated_company is not None  # Type narrowing for mypy/pyright
        self.assertEqual(updated_company.name, "Updated Name")
        self.assertEqual(updated_company.api_token, "updated-token")

    def test_execute_should_raise_error_when_company_not_found(self):
        """Test that execute raises error when company is not found."""
        input_data = UpdateCompanyInput(
            company_id=999,
            name="Updated Name",
            api_token="updated-token"
        )

        with self.assertRaises(CompanyNotFoundError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company with ID 999 not found", str(cm.exception))

    def test_execute_should_raise_error_when_name_is_empty(self):
        """Test that execute raises error when name is empty."""
        # Create company first
        company = Company(id=1, name="Original Name", api_token="original-token")
        self.repository.save(company)

        input_data = UpdateCompanyInput(company_id=1, name="", api_token="updated-token")

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company name is required", str(cm.exception))

    def test_execute_should_raise_error_when_api_token_is_empty(self):
        """Test that execute raises error when api_token is empty."""
        # Create company first
        company = Company(id=1, name="Original Name", api_token="original-token")
        self.repository.save(company)

        input_data = UpdateCompanyInput(company_id=1, name="Updated Name", api_token="")

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company API token is required", str(cm.exception))

    def test_execute_should_raise_error_when_name_conflicts_with_existing_company(self):
        """Test that execute raises error when new name conflicts with another company."""
        # Create two companies
        company1 = Company(id=1, name="Company One", api_token="token1")
        company2 = Company(id=2, name="Company Two", api_token="token2")
        self.repository.save(company1)
        self.repository.save(company2)

        # Try to update company1 with the name of company2
        input_data = UpdateCompanyInput(
            company_id=1,
            name="Company Two",  # This name already exists for company2
            api_token="updated-token"
        )

        with self.assertRaises(CompanyAlreadyExistsError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company with name 'Company Two' already exists", str(cm.exception))

    def test_execute_should_allow_updating_company_with_same_name(self):
        """Test that execute allows updating a company with its current name."""
        # Create company
        company = Company(id=1, name="Test Company", api_token="original-token")
        self.repository.save(company)

        # Update company keeping the same name but changing token
        input_data = UpdateCompanyInput(
            company_id=1,
            name="Test Company",  # Same name
            api_token="new-token"
        )

        result = self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        # Should succeed without error
        assert isinstance(result, Company)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "new-token")