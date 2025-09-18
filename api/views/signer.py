from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from api.base import BaseAPIViewSet
from core.orm.models import Signer
from core.repositories.signer_repo import DjangoSignerRepository
from core.app.providers.signer import SignerProvider
from api.serializers import SignerSerializer
from core.use_cases.signer.sync_signer_with_zapsign import (
    SyncSignerWithZapSignInput,
    SyncSignerWithZapSignOutput,
    SignerNotFoundError,
    SignerSyncError,
    CompanyNotFoundError,
)
from core.use_cases.signer.update_signer_in_zapsign import (
    UpdateSignerInZapSignInput,
    UpdateSignerInZapSignOutput,
    SignerNotFoundError as UpdateSignerNotFoundError,
    SignerUpdateError,
    CompanyNotFoundError as UpdateCompanyNotFoundError,
)
from core.use_cases.signer.remove_signer_from_zapsign import (
    RemoveSignerFromZapSignInput,
    RemoveSignerFromZapSignOutput,
    SignerNotFoundError as RemoveSignerNotFoundError,
    SignerRemovalError,
    CompanyNotFoundError as RemoveCompanyNotFoundError,
)
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


class SignerViewSet(BaseAPIViewSet):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signer_repo = DjangoSignerRepository()

    def list(self, request: Request) -> Response:
        """List all signers."""
        try:
            signers = self.signer_repo.find_all()
            serializer = SignerSerializer(signers, many=True)
            return self.success_response(
                data=serializer.data,
                message="Signers retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve signers: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request: Request, pk: Optional[str] = None) -> Response:
        """Get a specific signer by ID."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer = self.signer_repo.find_by_id(signer_id)
            if signer is None:
                return self.error_response(
                    message=f"Signer with ID {signer_id} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = SignerSerializer(signer)
            return self.success_response(
                data=serializer.data,
                message="Signer retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request: Request) -> Response:
        """Create a new signer."""
        serializer = SignerSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer = serializer.save()
            response_serializer = SignerSerializer(signer)
            return self.success_response(
                data=response_serializer.data,
                message="Signer created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to create signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request: Request, pk: Optional[str] = None) -> Response:
        """Update a signer."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        signer = self.signer_repo.find_by_id(signer_id)
        if signer is None:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SignerSerializer(signer, data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_signer = serializer.save()
            response_serializer = SignerSerializer(updated_signer)
            return self.success_response(
                data=response_serializer.data,
                message="Signer updated successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to update signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request: Request, pk: Optional[str] = None) -> Response:
        """Partially update a signer."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        signer = self.signer_repo.find_by_id(signer_id)
        if signer is None:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SignerSerializer(signer, data=request.data, partial=True)
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_signer = serializer.save()
            response_serializer = SignerSerializer(updated_signer)
            return self.success_response(
                data=response_serializer.data,
                message="Signer updated successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to update signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request: Request, pk: Optional[str] = None) -> Response:
        """Delete a signer."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check if signer exists
        signer = self.signer_repo.find_by_id(signer_id)
        if signer is None:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            # Use repository to delete
            success = self.signer_repo.delete_by_id(signer_id)
            if success:
                return self.success_response(
                    message="Signer deleted successfully",
                    status_code=status.HTTP_200_OK
                )
            else:
                return self.error_response(
                    message="Failed to delete signer",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return self.error_response(
                message=f"Failed to delete signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['put'], url_path='sync')
    def sync(self, request: Request, pk: Optional[str] = None) -> Response:
        """Sync a signer with ZapSign API to get latest status and data."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get use case from provider - be very explicit about types
            from core.use_cases.signer.sync_signer_with_zapsign import SyncSignerWithZapSignUseCase
            provider_result = SignerProvider.get_sync_signer_with_zapsign_use_case()
            sync_use_case: SyncSignerWithZapSignUseCase = provider_result

            # Create input data for synchronization
            input_data: SyncSignerWithZapSignInput = SyncSignerWithZapSignInput(signer_id=signer_id)

            # Execute synchronization using explicit method call
            execute_fn = getattr(sync_use_case, 'execute')
            result = execute_fn(input_data)
            # Type assertion to help Pyright understand the return type
            assert isinstance(result, SyncSignerWithZapSignOutput)

            # Serialize and return updated signer
            serializer = SignerSerializer(result.signer)
            return self.success_response(
                data=serializer.data,
                message="Signer synchronized successfully"
            )

        except SignerNotFoundError:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except SignerSyncError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except CompanyNotFoundError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAuthenticationError as e:
            return self.error_response(
                message=f"ZapSign authentication failed: {str(e)}",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except ZapSignValidationError as e:
            return self.error_response(
                message=f"ZapSign validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAPIError as e:
            return self.error_response(
                message=f"ZapSign API error: {str(e)}",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to sync signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='update-external')
    def update_external(self, request: Request, pk: Optional[str] = None) -> Response:
        """Update a signer in ZapSign API and sync locally."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get use case from provider - be very explicit about types
            from core.use_cases.signer.update_signer_in_zapsign import UpdateSignerInZapSignUseCase
            provider_result = SignerProvider.get_update_signer_in_zapsign_use_case()
            update_use_case: UpdateSignerInZapSignUseCase = provider_result

            # Execute update
            # Convert request data safely
            update_data: Dict[str, Any] = {}
            if hasattr(request, 'data') and request.data:
                # Handle DRF request.data which supports dict interface
                try:
                    # Cast to dict to handle various DRF data types
                    data = request.data
                    if hasattr(data, 'items'):
                        # Handle dict-like objects (most common case)
                        update_data = {str(k): v for k, v in data.items()}  # type: ignore
                    elif hasattr(data, 'dict'):
                        # Handle QueryDict objects specifically
                        update_data = data.dict()  # type: ignore
                    else:
                        update_data = {}
                except (TypeError, ValueError, AttributeError):
                    # Fallback for edge cases
                    update_data = {}

            # Create input data for update
            input_data: UpdateSignerInZapSignInput = UpdateSignerInZapSignInput(
                signer_id=signer_id,
                update_data=update_data
            )

            # Execute update using explicit method call
            execute_fn = getattr(update_use_case, 'execute')
            result = execute_fn(input_data)
            # Type assertion to help Pyright understand the return type
            assert isinstance(result, UpdateSignerInZapSignOutput)

            # Serialize and return updated signer
            serializer = SignerSerializer(result.signer)
            return self.success_response(
                data=serializer.data,
                message="Signer updated successfully in ZapSign"
            )

        except UpdateSignerNotFoundError:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except SignerUpdateError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except UpdateCompanyNotFoundError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAuthenticationError as e:
            return self.error_response(
                message=f"ZapSign authentication failed: {str(e)}",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except ZapSignValidationError as e:
            return self.error_response(
                message=f"ZapSign validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAPIError as e:
            return self.error_response(
                message=f"ZapSign API error: {str(e)}",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to update signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['delete'], url_path='remove-external')
    def remove_external(self, _request: Request, pk: Optional[str] = None) -> Response:
        """Remove a signer from ZapSign API and locally."""
        if pk is None:
            return self.error_response(
                message="Signer ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid signer ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get use case from provider - be very explicit about types
            from core.use_cases.signer.remove_signer_from_zapsign import RemoveSignerFromZapSignUseCase
            provider_result = SignerProvider.get_remove_signer_from_zapsign_use_case()
            remove_use_case: RemoveSignerFromZapSignUseCase = provider_result

            # Create input data for removal
            input_data: RemoveSignerFromZapSignInput = RemoveSignerFromZapSignInput(signer_id=signer_id)

            # Execute removal using explicit method call
            execute_fn = getattr(remove_use_case, 'execute')
            result = execute_fn(input_data)
            # Type assertion to help Pyright understand the return type
            assert isinstance(result, RemoveSignerFromZapSignOutput)

            # Format response
            response_data = {
                "success": result.success,
                "zapsign_removed": result.zapsign_removed,
                "locally_removed": result.locally_removed
            }

            return self.success_response(
                data=response_data,
                message="Signer removal completed"
            )

        except RemoveSignerNotFoundError:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except SignerRemovalError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except RemoveCompanyNotFoundError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAuthenticationError as e:
            return self.error_response(
                message=f"ZapSign authentication failed: {str(e)}",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except ZapSignValidationError as e:
            return self.error_response(
                message=f"ZapSign validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAPIError as e:
            return self.error_response(
                message=f"ZapSign API error: {str(e)}",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to remove signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )