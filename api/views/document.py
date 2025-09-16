from typing import Optional
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.base import BaseAPIViewSet
from core.orm.models import Company as CompanyModel
from core.orm.mappers import CompanyMapper
from core.domain.entities.company import Company
from api.serializers import DocumentSerializer
from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer
from core.app.providers.document import DocumentProvider
from core.use_cases.document.list_documents import ListDocumentsInput
from core.use_cases.document.get_document import GetDocumentInput
from core.use_cases.document.delete_document_with_zapsign import (
    DeleteDocumentWithZapSignInput,
    DocumentNotFoundError,
    DocumentAlreadyDeletedError
)
from core.services.exceptions import (
    ZapSignAuthenticationError,
    ZapSignValidationError,
    ZapSignAPIError,
)


def get_company_by_id(company_id: int) -> Optional[Company]:
    """Get company by ID."""
    try:
        company_model = CompanyModel.objects.get(id=company_id)
        return CompanyMapper.to_entity(company_model)
    except ObjectDoesNotExist:
        return None


class DocumentViewSet(BaseAPIViewSet):
    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        """List all documents (simplified version - no company filtering for now)."""
        try:
            # For now, get all documents since we don't have company context in the request
            # In a real application, this would be filtered by authenticated user's company
            use_case = DocumentProvider.get_list_documents_use_case()

            # Create a dummy company for listing (this should be improved with proper authentication)
            # For now, we'll list documents from all companies
            from core.repositories.document_repo import DjangoDocumentRepository
            repository = DjangoDocumentRepository()
            all_documents = repository.find_all()

            serializer = DocumentSerializer(all_documents, many=True)
            return self.success_response(
                data=serializer.data,
                message="Documents retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve documents: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request: Request, pk: Optional[str] = None) -> Response:
        """Get a specific document by ID."""
        if pk is None:
            return self.error_response(
                message="Document ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            document_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid document ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # For now, use direct repository access since we don't have company context
            # In a real application, this would use the GetDocumentUseCase with proper company authorization
            from core.repositories.document_repo import DjangoDocumentRepository
            repository = DjangoDocumentRepository()
            document = repository.find_by_id(document_id)

            if document is None:
                return self.error_response(
                    message="Document not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = DocumentSerializer(document)
            return self.success_response(
                data=serializer.data,
                message="Document retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve document: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request: Request) -> Response:
        """
        Create a document via ZapSign API integration.

        POST /api/documents/
        """
        try:
            # 1. Validate request data using ZapSign serializer
            zapsign_serializer = ZapSignDocumentCreateSerializer(data=request.data)
            if not zapsign_serializer.is_valid():
                return self.error_response(
                    message="Validation error",
                    data=zapsign_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # 2. Get company by ID from request
            validated_data = zapsign_serializer.validated_data
            assert isinstance(validated_data, dict), "Validated data must be a dictionary"
            company_id: int = int(validated_data["company_id"])
            company = get_company_by_id(company_id)
            if not company:
                return self.error_response(
                    message=f"Company with ID {company_id} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # 3. Convert to ZapSign request and execute use case
            from typing import cast
            document_serializer = cast(ZapSignDocumentCreateSerializer, zapsign_serializer)
            zapsign_request = document_serializer.to_zapsign_request()

            # 4. Execute use case (dependency injection via provider)
            use_case = DocumentProvider.get_create_document_use_case()
            result = use_case.execute(company=company, request=zapsign_request)

            # 5. Return response using standard Document serializer
            response_serializer = DocumentSerializer(result.document)
            return self.success_response(
                data=response_serializer.data,
                message="Document created successfully",
                status_code=status.HTTP_201_CREATED
            )

        except ZapSignAuthenticationError:
            return self.error_response(
                message="ZapSign authentication failed",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except ZapSignValidationError:
            return self.error_response(
                message="ZapSign validation error",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ZapSignAPIError:
            return self.error_response(
                message="ZapSign API error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception:
            return self.error_response(
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request: Request, pk=None) -> Response:
        """Update method is not supported."""
        return self.error_response(
            message="Update operation is not supported for documents",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request: Request, pk=None) -> Response:
        """Partial update method is not supported."""
        return self.error_response(
            message="Update operation is not supported for documents",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Delete a document with ZapSign integration.

        DELETE /api/documents/{id}/?deleted_by=user
        """
        if pk is None:
            return self.error_response(
                message="Document ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            document_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid document ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Get deleted_by from query parameters (defaulting to 'system')
        deleted_by = request.GET.get('deleted_by', 'system')

        try:
            # Execute use case with ZapSign integration
            use_case = DocumentProvider.get_delete_document_with_zapsign_use_case()
            input_data = DeleteDocumentWithZapSignInput(
                document_id=document_id,
                deleted_by=deleted_by
            )
            result = use_case.execute(input_data)

            # Format response
            response_data = {
                "document": {
                    "id": result.document.id,
                    "name": result.document.name,
                    "is_deleted": result.document.is_deleted,
                    "deleted_at": result.document.deleted_at.isoformat() if result.document.deleted_at else None,
                    "deleted_by": result.document.deleted_by,
                },
                "success": result.success,
                "zapsign_deleted": result.zapsign_deleted
            }

            return self.success_response(
                data=response_data,
                message="Document deleted successfully from both local database and ZapSign",
                status_code=status.HTTP_200_OK
            )

        except DocumentNotFoundError:
            return self.error_response(
                message="Document not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except DocumentAlreadyDeletedError:
            return self.error_response(
                message="Document is already deleted",
                status_code=status.HTTP_409_CONFLICT
            )
        except ZapSignAuthenticationError:
            return self.error_response(
                message="ZapSign authentication failed",
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
                message=f"Failed to delete document: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )