from typing import Optional
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.base import BaseAPIViewSet
from core.orm.models import Signer
from api.serializers import SignerSerializer


class SignerViewSet(BaseAPIViewSet):
    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        """List all signers."""
        try:
            signers = Signer.objects.all().order_by("-id")
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
            signer = Signer.objects.get(id=signer_id)
            serializer = SignerSerializer(signer)
            return self.success_response(
                data=serializer.data,
                message="Signer retrieved successfully"
            )
        except Signer.DoesNotExist:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
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

        try:
            signer = Signer.objects.get(id=signer_id)
        except Signer.DoesNotExist:
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

        try:
            signer = Signer.objects.get(id=signer_id)
        except Signer.DoesNotExist:
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

        try:
            signer = Signer.objects.get(id=signer_id)
            signer.delete()
            return self.success_response(
                message="Signer deleted successfully",
                status_code=status.HTTP_200_OK
            )
        except Signer.DoesNotExist:
            return self.error_response(
                message=f"Signer with ID {signer_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to delete signer: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )