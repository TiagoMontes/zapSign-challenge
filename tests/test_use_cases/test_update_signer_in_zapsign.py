"""Tests for UpdateSignerInZapSignUseCase."""

from unittest.mock import Mock
from django.test import TestCase
from core.domain.entities.signer import Signer
from core.domain.entities.company import Company
from core.domain.value_objects.zapsign_response import ZapSignSignerResponse
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class TestUpdateSignerInZapSignUseCase(TestCase):
    def setUp(self):
        # Mock repositories
        self.mock_signer_repo = Mock()
        self.mock_company_repo = Mock()
        self.mock_zapsign_service = Mock()

        # Create use case instance
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignUseCase
        self.use_case = UpdateSignerInZapSignUseCase(
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

        self.zapsign_response = ZapSignSignerResponse(
            token="signer-token-123",
            name="John Doe Updated",
            email="john.updated@example.com",
            status="pending",
            times_viewed=5
        )

    def test_update_signer_should_succeed_when_all_data_valid(self):
        """Test updating a signer successfully."""
        # Arrange
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.update_signer.return_value = self.zapsign_response

        updated_signer = Signer(
            id=1,
            name="John Doe Updated",
            email="john.updated@example.com",
            token="signer-token-123",
            company_id=1,
            status="pending",
            times_viewed=5
        )
        self.mock_signer_repo.save.return_value = updated_signer

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "John Doe Updated", "email": "john.updated@example.com"}
        )

        # Act
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignOutput
        result: UpdateSignerInZapSignOutput = self.use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.signer.name, "John Doe Updated")
        self.assertEqual(result.signer.email, "john.updated@example.com")
        self.assertEqual(result.signer.status, "pending")
        self.assertEqual(result.signer.times_viewed, 5)

        # Verify ZapSign API was called
        self.mock_zapsign_service.update_signer.assert_called_once_with(
            api_token="test-api-token",
            signer_token="signer-token-123",
            data={"name": "John Doe Updated", "email": "john.updated@example.com"}
        )

        # Verify signer was saved locally
        self.mock_signer_repo.save.assert_called_once()

    def test_update_signer_should_fail_when_signer_not_found(self):
        """Test updating a signer when signer doesn't exist."""
        from core.use_cases.signer.update_signer_in_zapsign import (
            UpdateSignerInZapSignInput,
            SignerNotFoundError
        )

        self.mock_signer_repo.find_by_id.return_value = None

        input_data = UpdateSignerInZapSignInput(
            signer_id=999,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(SignerNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_update_signer_should_fail_when_signer_has_no_token(self):
        """Test updating a signer when signer has no ZapSign token."""
        from core.use_cases.signer.update_signer_in_zapsign import (
            UpdateSignerInZapSignInput,
            SignerUpdateError
        )

        signer_without_token = Signer(
            id=1,
            name="John Doe",
            email="john@example.com",
            token="",  # No token
            company_id=1
        )

        self.mock_signer_repo.find_by_id.return_value = signer_without_token

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(SignerUpdateError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_update_signer_should_fail_when_company_not_found(self):
        """Test updating a signer when associated company doesn't exist."""
        from core.use_cases.signer.update_signer_in_zapsign import (
            UpdateSignerInZapSignInput,
            CompanyNotFoundError
        )

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = None

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(CompanyNotFoundError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_update_signer_should_propagate_zapsign_authentication_error(self):
        """Test that ZapSign authentication errors are propagated."""
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.update_signer.side_effect = ZapSignAuthenticationError(
            "Authentication failed"
        )

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(ZapSignAuthenticationError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_update_signer_should_propagate_zapsign_validation_error(self):
        """Test that ZapSign validation errors are propagated."""
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.update_signer.side_effect = ZapSignValidationError(
            "Validation failed"
        )

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(ZapSignValidationError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]

    def test_update_signer_should_propagate_zapsign_api_error(self):
        """Test that ZapSign API errors are propagated."""
        from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignInput

        self.mock_signer_repo.find_by_id.return_value = self.signer
        self.mock_company_repo.find_by_id.return_value = self.company
        self.mock_zapsign_service.update_signer.side_effect = ZapSignAPIError(
            "API error"
        )

        input_data = UpdateSignerInZapSignInput(
            signer_id=1,
            update_data={"name": "Updated Name"}
        )

        with self.assertRaises(ZapSignAPIError):
            self.use_case.execute(input_data)  # type: ignore[reportArgumentType]