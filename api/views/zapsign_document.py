"""ZapSign document creation API views."""

import logging
from typing import Optional, Any, Dict, cast
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.base import BaseAPIViewSet
from api.serializers.zapsign_document import (
    ZapSignDocumentCreateSerializer,
    ZapSignDocumentResponseSerializer,
)
from core.domain.entities.company import Company
from core.orm.models import Company as CompanyModel
from core.orm.mappers import CompanyMapper
from core.app.providers.document import DocumentProvider
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


class ZapSignDocumentViewSet(BaseAPIViewSet):
    """ViewSet for ZapSign document operations."""

    # Add empty queryset to avoid permission error
    queryset = None
    permission_classes = []  # Disable default permissions for this viewset

    def __init__(self, **kwargs):
        """Initialize viewset with injected dependencies."""
        super().__init__(**kwargs)
        self.create_document_use_case = DocumentProvider.get_create_document_use_case()

    def _get_company_from_request(self, company_id: int) -> Optional[Company]:
        """Get company by ID from request data."""
        return get_company_by_id(company_id)

    def create(self, request: Request) -> Response:
        """
        Create a document via ZapSign API.

        POST /api/v1/docs/
        """
        try:
            # 1. Validate request data
            serializer = ZapSignDocumentCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return self.error_response(
                    message="Validation error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    data=serializer.errors,
                )

            # 2. Get company by ID from request
            validated_data = serializer.validated_data
            assert isinstance(validated_data, dict), "Validated data must be a dictionary"
            company_id: int = int(validated_data["company_id"])
            company = self._get_company_from_request(company_id)
            if not company:
                return self.error_response(
                    message=f"Company with ID {company_id} not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # 3. Convert to ZapSign request
            # Type assertion: serializer is ZapSignDocumentCreateSerializer, not ListSerializer
            document_serializer = cast(ZapSignDocumentCreateSerializer, serializer)
            zapsign_request = document_serializer.to_zapsign_request()

            # 4. Execute use case (dependency injection via provider)
            result = self.create_document_use_case.execute(company=company, request=zapsign_request)

            # 5. Serialize response
            zapsign_response_serializer = ZapSignDocumentResponseSerializer(
                result.zapsign_response
            )

            response_data = {
                "document": {
                    "id": result.document.id,
                    "name": result.document.name,
                    "token": result.document.token,
                    "open_id": result.document.open_id,
                    "status": result.document.status,
                    "external_id": result.document.external_id,
                    "created_by": result.document.created_by,
                },
                "signers": [
                    {
                        "id": signer.id,
                        "name": signer.name,
                        "email": signer.email,
                        "token": signer.token,
                        "status": signer.status,
                        "external_id": signer.external_id,
                    }
                    for signer in result.signers
                ],
                "zapsign_response": zapsign_response_serializer.data,
            }

            return self.success_response(
                data=response_data,
                message="Document created successfully",
                status_code=status.HTTP_201_CREATED,
            )

        except ZapSignAuthenticationError as e:
            return self.error_response(
                message=f"ZapSign authentication failed: {str(e)}",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except ZapSignValidationError as e:
            return self.error_response(
                message=f"ZapSign validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except ZapSignAPIError as e:
            return self.error_response(
                message=f"ZapSign API error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            # Log the error for debugging
            logger = logging.getLogger(__name__)
            logger.exception(f"Unexpected error in ZapSign document creation: {str(e)}")
            return self.error_response(
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )