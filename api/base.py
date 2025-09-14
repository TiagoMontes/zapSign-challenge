from typing import Any, Dict
from rest_framework import viewsets, status
from rest_framework.response import Response


class BaseAPIViewSet(viewsets.ViewSet):
    """Base ViewSet with standardized response methods."""

    def success_response(
        self,
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """Create a standardized success response."""
        response_data: Dict[str, Any] = {
            "success": True,
            "code": status_code,
            "message": message
        }

        if data is not None:
            response_data["data"] = data

        return Response(response_data, status=status_code)

    def error_response(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ) -> Response:
        """Create a standardized error response."""
        response_data: Dict[str, Any] = {
            "success": False,
            "code": status_code,
            "message": message
        }

        if data is not None:
            response_data["data"] = data

        return Response(response_data, status=status_code)