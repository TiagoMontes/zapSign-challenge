from __future__ import annotations

from rest_framework import viewsets, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Any, Dict, cast

from core.domain.entities.signer import Signer as SignerEntity
from core.app.providers.signer import (
    get_create_signer_use_case,
    get_list_signers_use_case,
    get_get_signer_use_case,
    get_delete_signer_use_case,
)
from core.use_cases.signer.delete_signer import DeleteSignerUseCase
from api.serializers import SignerSerializer


class SignerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request: Request) -> Response:
        """List all signers using ListSignersUseCase"""
        use_case = get_list_signers_use_case()
        signers = use_case.execute()
        
        # Convert domain entities to response data
        data = []
        for signer in signers:
            data.append({
                'id': signer.id,
                'name': signer.name,
                'email': signer.email,
                'created_at': signer.created_at,
                'last_updated_at': signer.last_updated_at,
            })
        
        return Response(data)

    def create(self, request: Request) -> Response:
        """Create a new signer using CreateSignerUseCase"""
        serializer = SignerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get validated data with proper typing
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        # Create domain entity from validated data
        signer_entity = SignerEntity(
            id=None,
            name=validated_data['name'],
            email=validated_data['email'],
        )
        
        # Use the use case to create the signer
        use_case = get_create_signer_use_case()
        created_signer = use_case.execute(signer_entity)
        
        # Convert domain entity to response data
        response_data = {
            'id': created_signer.id,
            'name': created_signer.name,
            'email': created_signer.email,
            'created_at': created_signer.created_at,
            'last_updated_at': created_signer.last_updated_at,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Retrieve a specific signer using GetSignerUseCase"""
        if pk is None:
            return Response(
                {'error': 'Signer ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid signer ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_get_signer_use_case()
        signer = use_case.execute(signer_id)

        if signer is None:
            return Response(
                {'error': 'Signer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Convert domain entity to response data
        response_data = {
            'id': signer.id,
            'name': signer.name,
            'email': signer.email,
            'created_at': signer.created_at,
            'last_updated_at': signer.last_updated_at,
        }
        
        return Response(response_data)

    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Delete a signer using DeleteSignerUseCase"""
        if pk is None:
            return Response(
                {'error': 'Signer ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            signer_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid signer ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_delete_signer_use_case()
        use_case.execute(signer_id)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

