"""Tests for RemoveSignerFromZapSignUseCase."""

from unittest.mock import Mock
from django.test import TestCase
from core.domain.entities.signer import Signer
from core.domain.entities.company import Company
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class TestRemoveSignerFromZapSignUseCase(TestCase):
    def setUp(self):
        # Mock repositories
        self.mock_signer_repo = Mock()
        self.mock_company_repo = Mock()
        self.mock_zapsign_service = Mock()

        # Create use case instance
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignUseCase
        self.use_case = RemoveSignerFromZapSignUseCase(
            signer_repository=self.mock_signer_repo,
            company_repository=self.mock_company_repo,
            zapsign_service=self.mock_zapsign_service
        )

        # Test data
        self.company = Company(
            id=1,
            name="Test Company",
            api_token="test-api-token"
        )

        self.signer = Signer(
            id=1,
            name="John Doe",
            email="john@example.com",
            token="signer-token-123",
            company_id=1
        )

    def test_remove_signer_should_succeed_when_all_data_valid(self):
        """Test removing a signer successfully."""
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.remove_signer.return_value = True
        self.mock_signer_repo.delete_by_id.return_value = True

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        # Act
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignOutput
        result: RemoveSignerFromZapSignOutput = self.use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)
        self.assertTrue(result.zapsign_removed)
        self.assertTrue(result.locally_removed)

        # Verify ZapSign API was called
        self.mock_zapsign_service.remove_signer.assert_called_once_with(
            api_token="test-api-token",
            signer_token="signer-token-123"
        )

        # Verify signer was removed locally
        self.mock_signer_repo.delete_by_id.assert_called_once_with(1)

    def test_remove_signer_should_fail_when_signer_not_found(self):
        """Test removing a signer when signer doesn't exist."""
        from core.use_cases.signer.remove_signer_from_zapsign import (
            RemoveSignerFromZapSignInput,
            SignerNotFoundError
        )

        self.mock_signer_repo.find_by_id.return_value = None

        input_data = RemoveSignerFromZapSignInput(signer_id=999)

        with self.assertRaises(SignerNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_remove_signer_should_fail_when_signer_has_no_token(self):
        """Test removing a signer when signer has no ZapSign token."""
        from core.use_cases.signer.remove_signer_from_zapsign import (
            RemoveSignerFromZapSignInput,
            SignerRemovalError
        )

        signer_without_token = Signer(
            id=1,
            name="John Doe",
            email="john@example.com",
            token="",  # No token
            company_id=1
        )

        self.mock_signer_repo.find_by_id.return_value = signer_without_token

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        with self.assertRaises(SignerRemovalError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_remove_signer_should_fail_when_company_not_found(self):
        """Test removing a signer when associated company doesn't exist."""
        from core.use_cases.signer.remove_signer_from_zapsign import (
            RemoveSignerFromZapSignInput,
            CompanyNotFoundError
        )

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = None

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        with self.assertRaises(CompanyNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_remove_signer_should_handle_partial_failure_zapsign_fails(self):
        """Test handling when ZapSign removal fails but continue with local removal."""
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.remove_signer.side_effect = ZapSignValidationError(
            "Signer not found in ZapSign"
        )
        self.mock_signer_repo.delete_by_id.return_value = True

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        # Act
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignOutput
        result: RemoveSignerFromZapSignOutput = self.use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)  # Overall success despite ZapSign failure
        self.assertFalse(result.zapsign_removed)  # ZapSign removal failed
        self.assertTrue(result.locally_removed)  # Local removal succeeded

    def test_remove_signer_should_handle_partial_failure_local_fails(self):
        """Test handling when local removal fails after ZapSign succeeds."""
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.remove_signer.return_value = True
        self.mock_signer_repo.delete_by_id.return_value = False  # Local deletion fails

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        # Act
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignOutput
        result: RemoveSignerFromZapSignOutput = self.use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)  # Overall success despite local failure
        self.assertTrue(result.zapsign_removed)  # ZapSign removal succeeded
        self.assertFalse(result.locally_removed)  # Local removal failed

    def test_remove_signer_should_propagate_zapsign_authentication_error(self):
        """Test that ZapSign authentication errors are propagated."""
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.remove_signer.side_effect = ZapSignAuthenticationError(
            "Authentication failed"
        )

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        with self.assertRaises(ZapSignAuthenticationError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_remove_signer_should_propagate_zapsign_api_error(self):
        """Test that ZapSign API errors are propagated."""
        from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.remove_signer.side_effect = ZapSignAPIError(
            "API error"
        )

        input_data = RemoveSignerFromZapSignInput(signer_id=1)

        with self.assertRaises(ZapSignAPIError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]