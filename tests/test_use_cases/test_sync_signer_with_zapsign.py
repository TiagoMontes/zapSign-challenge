"""Tests for SyncSignerWithZapSignUseCase."""

import unittest
from datetime import datetime, timezone
from unittest.mock import Mock
from dataclasses import dataclass
from typing import Optional

from core.domain.entities.signer import Signer
from core.domain.entities.company import Company
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


@dataclass
class ZapSignSignerData:
    """Mock ZapSign signer response data."""
    token: str
    status: str
    times_viewed: Optional[int] = None
    last_view_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None


class TestSyncSignerWithZapSignUseCase(unittest.TestCase):
    """Test cases for SyncSignerWithZapSignUseCase."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Mock repositories
        self.signer_repository = Mock()
        self.company_repository = Mock()
        self.zapsign_service = Mock()

        # Test data
        self.signer_id = 1
        self.signer_token = "27c1018e-5f1a-4551-9a43-8b48104f1caa"
        self.company_id = 1
        self.api_token = "test_api_token"

        # Create test signer with old data
        self.existing_signer = Signer(
            id=self.signer_id,
            name="Test Signer",
            email="test@example.com",
            token=self.signer_token,
            status="new",
            company_id=self.company_id,
            created_at=datetime.now(timezone.utc),
            last_updated_at=datetime.now(timezone.utc),
            times_viewed=None,
            last_view_at=None,
            signed_at=None,
        )

        # Create test company
        self.company = Company(
            id=self.company_id,
            name="Test Company",
            api_token=self.api_token,
            created_at=datetime.now(timezone.utc),
            last_updated_at=datetime.now(timezone.utc),
        )

        # Configure repository mocks
        self.signer_repository.find_by_id.return_value = self.existing_signer
        self.company_repository.find_by_id.return_value = self.company

    def test_execute_should_sync_signer_data_successfully_when_valid_request(self) -> None:
        """Test successful signer synchronization."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
        )

        from core.domain.value_objects.zapsign_response import ZapSignSignerResponse

        updated_zapsign_data = ZapSignSignerResponse(
            token=self.signer_token,
            name="Test Signer",
            email="test@example.com",
            status="link-opened",
            times_viewed=5,
            last_view_at=datetime.now(timezone.utc).isoformat(),
            signed_at=None,
        )

        self.zapsign_service.get_signer_by_token.return_value = updated_zapsign_data

        updated_signer = Signer(
            id=self.signer_id,
            name="Test Signer",
            email="test@example.com",
            token=self.signer_token,
            status="link-opened",
            company_id=self.company_id,
            created_at=self.existing_signer.created_at,
            last_updated_at=datetime.now(timezone.utc),
            times_viewed=5,
            last_view_at=datetime.now(timezone.utc),
            signed_at=None,
        )
        self.signer_repository.save.return_value = updated_signer

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act
        from core.use_cases.signer.sync_signer_with_zapsign import SyncSignerWithZapSignOutput
        result: SyncSignerWithZapSignOutput = use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.signer.status, "link-opened")
        self.assertEqual(result.signer.times_viewed, 5)
        self.assertIsNotNone(result.signer.last_view_at)
        self.assertIsNone(result.signer.signed_at)

        # Verify method calls
        self.signer_repository.find_by_id.assert_called_once_with(self.signer_id)
        self.company_repository.find_by_id.assert_called_once_with(self.company_id)
        self.zapsign_service.get_signer_by_token.assert_called_once_with(
            api_token=self.api_token,
            signer_token=self.signer_token
        )
        self.signer_repository.save.assert_called_once()

    def test_execute_should_raise_error_when_signer_not_found(self) -> None:
        """Test error when signer is not found."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
            SignerNotFoundError,
        )

        self.signer_repository.find_by_id.return_value = None

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=999)

        # Act & Assert
        with self.assertRaises(SignerNotFoundError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Signer not found")

    def test_execute_should_raise_error_when_signer_has_no_token(self) -> None:
        """Test error when signer has no token."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
            SignerSyncError,
        )

        signer_without_token = Signer(
            id=self.signer_id,
            name="Test Signer",
            email="test@example.com",
            token="",  # Empty token
            status="new",
        )
        self.signer_repository.find_by_id.return_value = signer_without_token

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act & Assert
        with self.assertRaises(SignerSyncError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Signer has no token for ZapSign sync")

    def test_execute_should_raise_error_when_company_not_found(self) -> None:
        """Test error when company is not found."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
            CompanyNotFoundError,
        )

        # Add company_id to signer - we need this field in signer entity
        self.existing_signer.company_id = self.company_id
        self.company_repository.find_by_id.return_value = None

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act & Assert
        with self.assertRaises(CompanyNotFoundError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Associated company not found")

    def test_execute_should_propagate_zapsign_authentication_error(self) -> None:
        """Test that ZapSign authentication errors are propagated."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
        )

        self.existing_signer.company_id = self.company_id
        self.zapsign_service.get_signer_by_token.side_effect = ZapSignAuthenticationError("Invalid API token")

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act & Assert
        with self.assertRaises(ZapSignAuthenticationError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Invalid API token")

    def test_execute_should_propagate_zapsign_validation_error(self) -> None:
        """Test that ZapSign validation errors are propagated."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
        )

        self.existing_signer.company_id = self.company_id
        self.zapsign_service.get_signer_by_token.side_effect = ZapSignValidationError("Invalid signer token")

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act & Assert
        with self.assertRaises(ZapSignValidationError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Invalid signer token")

    def test_execute_should_propagate_zapsign_api_error(self) -> None:
        """Test that ZapSign API errors are propagated."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
        )

        self.existing_signer.company_id = self.company_id
        self.zapsign_service.get_signer_by_token.side_effect = ZapSignAPIError("Service unavailable")

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act & Assert
        with self.assertRaises(ZapSignAPIError) as context:
            use_case.execute(input_data)  # type: ignore[reportArgumentType]

        self.assertEqual(str(context.exception), "Service unavailable")

    def test_execute_should_sync_signed_signer_data_when_signed(self) -> None:
        """Test synchronization of a signed signer."""
        # Arrange
        from core.use_cases.signer.sync_signer_with_zapsign import (
            SyncSignerWithZapSignUseCase,
            SyncSignerWithZapSignInput,
        )

        from core.domain.value_objects.zapsign_response import ZapSignSignerResponse

        self.existing_signer.company_id = self.company_id
        signed_time = datetime.now(timezone.utc)

        signed_zapsign_data = ZapSignSignerResponse(
            token=self.signer_token,
            name="Test Signer",
            email="test@example.com",
            status="signed",
            times_viewed=10,
            last_view_at=datetime.now(timezone.utc).isoformat(),
            signed_at=signed_time.isoformat(),
        )

        self.zapsign_service.get_signer_by_token.return_value = signed_zapsign_data

        updated_signer = Signer(
            id=self.signer_id,
            name="Test Signer",
            email="test@example.com",
            token=self.signer_token,
            status="signed",
            company_id=self.company_id,
            created_at=self.existing_signer.created_at,
            last_updated_at=datetime.now(timezone.utc),
            times_viewed=10,
            last_view_at=datetime.now(timezone.utc),
            signed_at=signed_time,
        )
        self.signer_repository.save.return_value = updated_signer

        use_case = SyncSignerWithZapSignUseCase(
            signer_repository=self.signer_repository,
            company_repository=self.company_repository,
            zapsign_service=self.zapsign_service,
        )

        input_data = SyncSignerWithZapSignInput(signer_id=self.signer_id)

        # Act
        from core.use_cases.signer.sync_signer_with_zapsign import SyncSignerWithZapSignOutput
        result: SyncSignerWithZapSignOutput = use_case.execute(input_data)  # type: ignore[assignment]

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.signer.status, "signed")
        self.assertEqual(result.signer.times_viewed, 10)
        self.assertIsNotNone(result.signer.signed_at)


if __name__ == "__main__":
    unittest.main()