"""Tests for DocumentProvider DI container."""

from django.test import TestCase
from unittest.mock import patch, MagicMock

from core.app.providers.document import DocumentProvider
from core.services.zapsign_service import ZapSignService
from core.repositories.document_repo import DjangoDocumentRepository
from core.repositories.signer_repo import DjangoSignerRepository
from core.use_cases.document.create_document_from_upload import CreateDocumentFromUploadUseCase


class TestDocumentProvider(TestCase):
    """Test cases for DocumentProvider."""

    def test_get_zapsign_service_should_return_zapsign_service_instance(self):
        """Test that get_zapsign_service returns a ZapSignService instance."""
        service = DocumentProvider.get_zapsign_service()
        assert isinstance(service, ZapSignService)

    def test_get_zapsign_service_should_return_same_instance_on_multiple_calls(self):
        """Test that get_zapsign_service returns the same instance (singleton pattern)."""
        service1 = DocumentProvider.get_zapsign_service()
        service2 = DocumentProvider.get_zapsign_service()
        assert service1 is service2

    def test_get_document_repository_should_return_django_document_repository_instance(self):
        """Test that get_document_repository returns a DjangoDocumentRepository instance."""
        repository = DocumentProvider.get_document_repository()
        assert isinstance(repository, DjangoDocumentRepository)

    def test_get_document_repository_should_return_same_instance_on_multiple_calls(self):
        """Test that get_document_repository returns the same instance (singleton pattern)."""
        repo1 = DocumentProvider.get_document_repository()
        repo2 = DocumentProvider.get_document_repository()
        assert repo1 is repo2

    def test_get_signer_repository_should_return_django_signer_repository_instance(self):
        """Test that get_signer_repository returns a DjangoSignerRepository instance."""
        repository = DocumentProvider.get_signer_repository()
        assert isinstance(repository, DjangoSignerRepository)

    def test_get_signer_repository_should_return_same_instance_on_multiple_calls(self):
        """Test that get_signer_repository returns the same instance (singleton pattern)."""
        repo1 = DocumentProvider.get_signer_repository()
        repo2 = DocumentProvider.get_signer_repository()
        assert repo1 is repo2

    def test_get_create_document_use_case_should_return_configured_use_case(self):
        """Test that get_create_document_use_case returns a properly configured use case."""
        use_case = DocumentProvider.get_create_document_use_case()
        assert isinstance(use_case, CreateDocumentFromUploadUseCase)

        # Verify dependencies are properly injected
        assert isinstance(use_case.zapsign_service, ZapSignService)
        assert isinstance(use_case.document_repository, DjangoDocumentRepository)
        assert isinstance(use_case.signer_repository, DjangoSignerRepository)

    def test_get_create_document_use_case_should_use_singleton_dependencies(self):
        """Test that use case uses singleton instances of dependencies."""
        use_case1 = DocumentProvider.get_create_document_use_case()
        use_case2 = DocumentProvider.get_create_document_use_case()

        # Use cases should be different instances (not singleton themselves)
        assert use_case1 is not use_case2

        # But their dependencies should be the same (singleton)
        assert use_case1.zapsign_service is use_case2.zapsign_service
        assert use_case1.document_repository is use_case2.document_repository
        assert use_case1.signer_repository is use_case2.signer_repository

    @patch('core.app.providers.document.DocumentProvider.get_zapsign_service')
    @patch('core.app.providers.document.DocumentProvider.get_document_repository')
    @patch('core.app.providers.document.DocumentProvider.get_signer_repository')
    def test_get_create_document_use_case_should_be_mockable_for_testing(
        self, mock_signer_repo, mock_doc_repo, mock_zapsign_service
    ):
        """Test that the provider methods can be mocked for testing purposes."""
        # Arrange
        mock_zapsign = MagicMock()
        mock_doc_repo_instance = MagicMock()
        mock_signer_repo_instance = MagicMock()

        mock_zapsign_service.return_value = mock_zapsign
        mock_doc_repo.return_value = mock_doc_repo_instance
        mock_signer_repo.return_value = mock_signer_repo_instance

        # Act
        use_case = DocumentProvider.get_create_document_use_case()

        # Assert
        assert use_case.zapsign_service is mock_zapsign
        assert use_case.document_repository is mock_doc_repo_instance
        assert use_case.signer_repository is mock_signer_repo_instance

    def test_clear_cache_should_reset_singleton_instances(self):
        """Test that clear_cache resets all singleton instances."""
        # Get initial instances
        service1 = DocumentProvider.get_zapsign_service()
        doc_repo1 = DocumentProvider.get_document_repository()
        signer_repo1 = DocumentProvider.get_signer_repository()

        # Clear cache
        DocumentProvider.clear_cache()

        # Get new instances
        service2 = DocumentProvider.get_zapsign_service()
        doc_repo2 = DocumentProvider.get_document_repository()
        signer_repo2 = DocumentProvider.get_signer_repository()

        # Instances should be different after cache clear
        self.assertIsNot(service1, service2)
        self.assertIsNot(doc_repo1, doc_repo2)
        self.assertIsNot(signer_repo1, signer_repo2)