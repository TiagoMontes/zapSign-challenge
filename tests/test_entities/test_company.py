from django.test import TestCase
from core.domain.entities.company import Company


class TestCompanyEntity(TestCase):
    """Test Company entity domain validation and behavior."""

    def test_create_company_should_succeed_when_required_fields_provided(self):
        """Test that a company can be created with required fields."""
        company = Company(name="Test Company", api_token="test-token")

        self.assertEqual(company.name, "Test Company")
        self.assertEqual(company.api_token, "test-token")
        self.assertIsNone(company.id)
        self.assertIsNone(company.created_at)
        self.assertIsNone(company.last_updated_at)

    def test_company_should_require_name_when_creating(self):
        """Test that company name is required."""
        with self.assertRaises(TypeError):
            Company(api_token="test-token")  # type: ignore[reportCallIssue]  # Missing name parameter

    def test_company_should_require_api_token_when_creating(self):
        """Test that company api_token is required."""
        with self.assertRaises(TypeError):
            Company(name="Test Company")  # type: ignore[reportCallIssue]  # Missing api_token parameter

    def test_company_should_validate_name_is_not_empty_when_creating(self):
        """Test that company name cannot be empty string."""
        company = Company(name="", api_token="test-token")

        self.assertFalse(company.is_valid())
        self.assertIn("name", company.get_validation_errors())

    def test_company_should_validate_api_token_is_not_empty_when_creating(self):
        """Test that company api_token cannot be empty string."""
        company = Company(name="Test Company", api_token="")

        self.assertFalse(company.is_valid())
        self.assertIn("api_token", company.get_validation_errors())

    def test_company_should_be_valid_when_all_required_fields_provided(self):
        """Test that company is valid when all required fields are provided."""
        company = Company(name="Test Company", api_token="test-token")

        self.assertTrue(company.is_valid())
        self.assertEqual(len(company.get_validation_errors()), 0)

    def test_company_should_allow_name_with_255_characters_when_creating(self):
        """Test that company name can be up to 255 characters."""
        long_name = "A" * 255
        company = Company(name=long_name, api_token="test-token")

        self.assertTrue(company.is_valid())
        self.assertEqual(company.name, long_name)

    def test_company_should_reject_name_longer_than_255_characters_when_creating(self):
        """Test that company name cannot be longer than 255 characters."""
        long_name = "A" * 256
        company = Company(name=long_name, api_token="test-token")

        self.assertFalse(company.is_valid())
        self.assertIn("name", company.get_validation_errors())

    def test_company_should_allow_api_token_with_255_characters_when_creating(self):
        """Test that company api_token can be up to 255 characters."""
        long_token = "T" * 255
        company = Company(name="Test Company", api_token=long_token)

        self.assertTrue(company.is_valid())
        self.assertEqual(company.api_token, long_token)

    def test_company_should_reject_api_token_longer_than_255_characters_when_creating(self):
        """Test that company api_token cannot be longer than 255 characters."""
        long_token = "T" * 256
        company = Company(name="Test Company", api_token=long_token)

        self.assertFalse(company.is_valid())
        self.assertIn("api_token", company.get_validation_errors())