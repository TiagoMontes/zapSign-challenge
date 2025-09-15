"""Integration tests for ViewSet with DI container."""

from django.test import TestCase
from unittest.mock import patch

from api.views.zapsign_document import ZapSignDocumentViewSet
from core.use_cases.document.create_document_from_upload import CreateDocumentFromUploadUseCase


class TestZapSignDocumentViewSetIntegration(TestCase):
    """Test cases for ZapSignDocumentViewSet DI integration."""

    def test_viewset_should_initialize_with_injected_use_case(self):
        """Test that viewset initializes with use case from DI container."""
        viewset = ZapSignDocumentViewSet()

        # Verify use case is properly injected
        self.assertIsInstance(viewset.create_document_use_case, CreateDocumentFromUploadUseCase)

        # Verify dependencies are properly injected in the use case
        self.assertIsNotNone(viewset.create_document_use_case.zapsign_service)
        self.assertIsNotNone(viewset.create_document_use_case.document_repository)
        self.assertIsNotNone(viewset.create_document_use_case.signer_repository)

    @patch('core.app.providers.document.DocumentProvider.get_create_document_use_case')
    def test_viewset_should_use_provider_for_dependency_injection(self, mock_get_use_case):
        """Test that viewset uses DocumentProvider for dependency injection."""
        from unittest.mock import MagicMock

        # Arrange
        mock_use_case = MagicMock(spec=CreateDocumentFromUploadUseCase)
        mock_get_use_case.return_value = mock_use_case

        # Act
        viewset = ZapSignDocumentViewSet()

        # Assert
        mock_get_use_case.assert_called_once()
        self.assertIs(viewset.create_document_use_case, mock_use_case)

    def test_singleton_behavior_across_multiple_viewset_instances(self):
        """Test that singleton dependencies are shared across ViewSet instances."""
        viewset1 = ZapSignDocumentViewSet()
        viewset2 = ZapSignDocumentViewSet()

        # Use cases should be different instances (not singleton themselves)
        self.assertIsNot(viewset1.create_document_use_case, viewset2.create_document_use_case)

        # But their dependencies should be the same (singleton)
        self.assertIs(
            viewset1.create_document_use_case.zapsign_service,
            viewset2.create_document_use_case.zapsign_service
        )
        self.assertIs(
            viewset1.create_document_use_case.document_repository,
            viewset2.create_document_use_case.document_repository
        )
        self.assertIs(
            viewset1.create_document_use_case.signer_repository,
            viewset2.create_document_use_case.signer_repository
        )