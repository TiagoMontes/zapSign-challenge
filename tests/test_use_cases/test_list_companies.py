from django.test import TestCase
from core.domain.entities.company import Company
from core.use_cases.company.list_companies import ListCompanies
from tests.fakes.company_repo import FakeCompanyRepository


class TestListCompaniesUseCase(TestCase):
    """Test List Companies use case."""

    def setUp(self):
        """Set up test data."""
        self.repository = FakeCompanyRepository()
        self.use_case = ListCompanies(self.repository)

    def test_execute_should_return_all_companies_ordered_by_id_desc(self):
        """Test that execute returns all companies ordered by ID descending."""
        # Create companies
        company1 = Company(id=1, name="Company 1", api_token="token1")
        company2 = Company(id=2, name="Company 2", api_token="token2")
        company3 = Company(id=3, name="Company 3", api_token="token3")

        self.repository.save(company1)
        self.repository.save(company2)
        self.repository.save(company3)

        result = self.use_case.execute()

        self.assertEqual(len(result), 3)
        # Should be ordered by ID descending
        self.assertEqual(result[0].id, 3)
        self.assertEqual(result[1].id, 2)
        self.assertEqual(result[2].id, 1)

    def test_execute_should_return_empty_list_when_no_companies(self):
        """Test that execute returns empty list when no companies exist."""
        result = self.use_case.execute()

        self.assertEqual(len(result), 0)