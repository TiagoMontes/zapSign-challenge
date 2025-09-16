from django.test import TestCase
from core.domain.entities.company import Company
from core.use_cases.company.create_company import CreateCompany, CreateCompanyInput
from core.use_cases.company.exceptions import CompanyAlreadyExistsError, CompanyValidationError
from tests.fakes.company_repo import FakeCompanyRepository


class TestCreateCompanyUseCase(TestCase):
    """Test Create Company use case."""

    def setUp(self):
        """Set up test data."""
        self.repository = FakeCompanyRepository()
        self.use_case = CreateCompany(self.repository)

    def test_execute_should_create_company_when_valid_input_provided(self):
        """Test that execute creates company when valid input is provided."""
        input_data = CreateCompanyInput(name="Test Company", api_token="test-token")

        result = self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        # Type narrowing to help Pyright understand the return type
        assert isinstance(result, Company)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.name, "Test Company")
        self.assertEqual(result.api_token, "test-token")
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.last_updated_at)

        # Verify company is saved in repository
        assert result.id is not None  # Type narrowing for Pyright
        saved_company = self.repository.find_by_id(result.id)
        self.assertIsNotNone(saved_company)
        assert saved_company is not None  # Type narrowing for Pyright
        self.assertEqual(saved_company.name, "Test Company")

    def test_execute_should_raise_error_when_name_is_empty(self):
        """Test that execute raises error when name is empty."""
        input_data = CreateCompanyInput(name="", api_token="test-token")

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company name is required", str(cm.exception))

    def test_execute_should_raise_error_when_api_token_is_empty(self):
        """Test that execute raises error when api_token is empty."""
        input_data = CreateCompanyInput(name="Test Company", api_token="")

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company API token is required", str(cm.exception))

    def test_execute_should_raise_error_when_name_too_long(self):
        """Test that execute raises error when name is too long."""
        long_name = "A" * 256
        input_data = CreateCompanyInput(name=long_name, api_token="test-token")

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company name cannot be longer than 255 characters", str(cm.exception))

    def test_execute_should_raise_error_when_api_token_too_long(self):
        """Test that execute raises error when api_token is too long."""
        long_token = "T" * 256
        input_data = CreateCompanyInput(name="Test Company", api_token=long_token)

        with self.assertRaises(CompanyValidationError) as cm:
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertIn("Company API token cannot be longer than 255 characters", str(cm.exception))

    def test_execute_should_raise_error_when_company_name_already_exists(self):
        """Test that execute raises error when company name already exists."""
        # First, create a company
        existing_input = CreateCompanyInput(name="Existing Company", api_token="existing-token")
        self.use_case.execute(existing_input)  # type: ignore[reportArgumentType]

        # Try to create another company with the same name
        duplicate_input = CreateCompanyInput(name="Existing Company", api_token="new-token")

        with self.assertRaises(CompanyAlreadyExistsError) as cm:
            self.use_case.execute(duplicate_input)  # type: ignore[reportArgumentType]

        self.assertIn("Company with name 'Existing Company' already exists", str(cm.exception))
