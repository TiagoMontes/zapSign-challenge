from __future__ import annotations

from rest_framework import viewsets, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Any, Dict, cast

from core.domain.entities.company import Company as CompanyEntity
from core.app.providers.company import (
    get_create_company_use_case,
    get_list_companies_use_case,
    get_get_company_use_case,
    get_delete_company_use_case,
)
from core.use_cases.company.delete_company import DeleteCompanyUseCase
from api.serializers import CompanySerializer


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request: Request) -> Response:
        use_case = get_list_companies_use_case()
        companies = use_case.execute()
        
        data = []
        for company in companies:
            data.append({
                'id': company.id,
                'name': company.name,
                'api_token': company.api_token,
                'created_at': company.created_at,
                'last_updated_at': company.last_updated_at,
            })
        
        return Response(data)

    def create(self, request: Request) -> Response:
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        company_entity = CompanyEntity(
            id=None,
            name=validated_data['name'],
            api_token=validated_data.get('api_token', ''),
        )

        use_case = get_create_company_use_case()
        created_company = use_case.execute(company_entity)

        response_data = {
            'id': created_company.id,
            'name': created_company.name,
            'api_token': created_company.api_token,
            'created_at': created_company.created_at,
            'last_updated_at': created_company.last_updated_at,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        if pk is None:
            return Response(
                {'error': 'Company ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid company ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_get_company_use_case()
        company = use_case.execute(company_id)

        if company is None:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        response_data = {
            'id': company.id,
            'name': company.name,
            'api_token': company.api_token,
            'created_at': company.created_at,
            'last_updated_at': company.last_updated_at,
        }
        
        return Response(response_data)

    def destroy(self, request: Request, pk: str | None = None) -> Response:
        if pk is None:
            return Response(
                {'error': 'Company ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid company ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_delete_company_use_case()
        use_case.execute(company_id)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

