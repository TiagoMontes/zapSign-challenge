from typing import Any, Dict, Optional, cast
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from api.base import BaseAPIViewSet
from api.serializers import CompanySerializer
from core.repositories.company_repo import CompanyRepository
from core.use_cases.company.create_company import CreateCompany, CreateCompanyInput
from core.use_cases.company.get_company import GetCompany, GetCompanyInput
from core.use_cases.company.list_companies import ListCompanies
from core.use_cases.company.update_company import UpdateCompany, UpdateCompanyInput
from core.use_cases.company.delete_company import DeleteCompany, DeleteCompanyInput


class CompanyViewSet(BaseAPIViewSet):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._repository = CompanyRepository()

    def list(self, request: Request) -> Response:
        """List all companies."""
        try:
            use_case = ListCompanies(self._repository)
            companies = use_case.execute()
            serializer = CompanySerializer(companies, many=True)
            return self.success_response(
                data=serializer.data,
                message="Companies retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve companies: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request: Request) -> Response:
        """Create a new company."""
        serializer = CompanySerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated_data = cast(Dict[str, Any], serializer.validated_data)
        if not validated_data:
            return self.error_response(
                message="No valid data provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = CreateCompany(self._repository)
            input_data = CreateCompanyInput(
                name=validated_data['name'],
                api_token=validated_data['api_token']
            )
            company = use_case.execute(input_data)  # type: ignore[reportArgumentType]
            response_serializer = CompanySerializer(company)
            return self.success_response(
                data=response_serializer.data,
                message="Company created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to create company: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request: Request, pk: Optional[str] = None) -> Response:
        """Get a specific company by ID."""
        if pk is None:
            return self.error_response(
                message="Company ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            company_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid company ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = GetCompany(self._repository)
            input_data = GetCompanyInput(company_id=company_id)
            company = use_case.execute(input_data)  # type: ignore[reportArgumentType]
            serializer = CompanySerializer(company)
            return self.success_response(
                data=serializer.data,
                message="Company retrieved successfully"
            )
        except ValueError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to retrieve company: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request: Request, pk: Optional[str] = None) -> Response:
        """Update a company."""
        if pk is None:
            return self.error_response(
                message="Company ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            company_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid company ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanySerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated_data = cast(Dict[str, Any], serializer.validated_data)
        if not validated_data:
            return self.error_response(
                message="No valid data provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = UpdateCompany(self._repository)
            input_data = UpdateCompanyInput(
                company_id=company_id,
                name=validated_data['name'],
                api_token=validated_data['api_token']
            )
            company = use_case.execute(input_data)  # type: ignore[reportArgumentType]
            response_serializer = CompanySerializer(company)
            return self.success_response(
                data=response_serializer.data,
                message="Company updated successfully"
            )
        except ValueError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to update company: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request: Request, pk: Optional[str] = None) -> Response:
        """Partially update a company (same as full update for this implementation)."""
        return self.update(request, pk)

    def destroy(self, request: Request, pk: Optional[str] = None) -> Response:
        """Delete a company."""
        if pk is None:
            return self.error_response(
                message="Company ID is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            company_id = int(pk)
        except (ValueError, TypeError):
            return self.error_response(
                message="Invalid company ID format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = DeleteCompany(self._repository)
            input_data = DeleteCompanyInput(company_id=company_id)
            use_case.execute(input_data)  # type: ignore[reportArgumentType]
            return self.success_response(
                message="Company deleted successfully",
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to delete company: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )