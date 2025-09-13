from __future__ import annotations

from rest_framework import viewsets, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Any, Dict, List, cast

from core.domain.entities.document import Document as DocumentEntity
from core.app.providers.document import (
    get_create_document_use_case,
    get_list_documents_use_case,
    get_get_document_use_case,
    get_delete_document_use_case,
)
from core.use_cases.document.create_document import CreateDocumentUseCase
from core.use_cases.document.delete_document import DeleteDocumentUseCase
from api.serializers import DocumentSerializer


class DocumentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request: Request) -> Response:
        """List all documents using ListDocumentsUseCase"""
        use_case = get_list_documents_use_case()
        documents = use_case.execute()
        
        # Convert domain entities to response data
        data = []
        for document in documents:
            data.append({
                'id': document.id,
                'name': document.name,
                'company': document.company_id,
                'signers': list(document.signer_ids or []),
                'status': document.status,
                'token': document.token,
                'open_id': document.open_id,
                'created_by': document.created_by,
                'external_id': document.external_id,
                'created_at': document.created_at,
                'last_updated_at': document.last_updated_at,
            })
        
        return Response(data)

    def create(self, request: Request) -> Response:
        """Create a new document using CreateDocumentUseCase"""
        serializer = DocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get validated data with proper typing
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        # Create domain entity from validated data
        document_entity = DocumentEntity(
            id=None,
            name=validated_data['name'],
            company_id=validated_data['company'],
            signer_ids=validated_data.get('signers', []),
        )
        
        # Use the use case to create the document
        use_case = get_create_document_use_case()
        created_document = use_case.execute(document_entity)
        
        # Convert domain entity to response data
        response_data = {
            'id': created_document.id,
            'name': created_document.name,
            'company': created_document.company_id,
            'signers': list(created_document.signer_ids or []),
            'status': created_document.status,
            'token': created_document.token,
            'open_id': created_document.open_id,
            'created_by': created_document.created_by,
            'external_id': created_document.external_id,
            'created_at': created_document.created_at,
            'last_updated_at': created_document.last_updated_at,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Retrieve a specific document using GetDocumentUseCase"""
        if pk is None:
            return Response(
                {'error': 'Document ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid document ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_get_document_use_case()
        document = use_case.execute(document_id)
        
        if document is None:
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Convert domain entity to response data
        response_data = {
            'id': document.id,
            'name': document.name,
            'company': document.company_id,
            'signers': list(document.signer_ids or []),
            'status': document.status,
            'token': document.token,
            'open_id': document.open_id,
            'created_by': document.created_by,
            'external_id': document.external_id,
            'created_at': document.created_at,
            'last_updated_at': document.last_updated_at,
        }
        
        return Response(response_data)

    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Delete a document using DeleteDocumentUseCase"""
        if pk is None:
            return Response(
                {'error': 'Document ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document_id = int(pk)
        except ValueError:
            return Response(
                {'error': 'Invalid document ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = get_delete_document_use_case()
        use_case.execute(document_id)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

