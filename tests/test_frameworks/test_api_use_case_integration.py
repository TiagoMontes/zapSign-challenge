"""
Test integration between API layer and Use Cases.
These tests ensure that API views properly use Use Cases instead of direct ORM access.
"""
from unittest.mock import Mock, patch
from typing import Any, cast

from rest_framework.test import APITestCase
from rest_framework.response import Response

from core.domain.entities.company import Company as CompanyEntity
from core.domain.entities.document import Document as DocumentEntity
from core.domain.entities.signer import Signer as SignerEntity


class ApiUsesCaseIntegrationTests(APITestCase):
    """Test that API layer properly integrates with Use Cases"""
    
    @patch('core.app.providers.company.get_create_company_use_case')
    @patch('core.app.providers.company.get_list_companies_use_case')
    def test_company_post_should_use_create_company_use_case(
        self, 
        mock_list_use_case: Mock,
        mock_create_use_case: Mock
    ):
        """Test that POST /api/companies/ uses CreateCompanyUseCase"""
        # Arrange
        mock_create_instance = Mock()
        mock_create_use_case.return_value = mock_create_instance
        
        expected_company = CompanyEntity(
            id=1,
            name="Test Company",
            api_token="test-token-123"
        )
        mock_create_instance.execute.return_value = expected_company
        
        # Act
        response = cast(Response, self.client.post(
            "/api/companies/",
            {"name": "Test Company"},
            format="json"
        ))
        
        # Assert
        self.assertEqual(response.status_code, 201)
        mock_create_use_case.assert_called_once()
        mock_create_instance.execute.assert_called_once()
        
        # Verify the use case was called with correct entity
        call_args = mock_create_instance.execute.call_args[0][0]
        self.assertEqual(call_args.name, "Test Company")
        self.assertIsNone(call_args.id)  # ID should be None for creation
    
    @patch('core.app.providers.company.get_list_companies_use_case')
    def test_company_get_should_use_list_companies_use_case(
        self,
        mock_list_use_case: Mock
    ):
        """Test that GET /api/companies/ uses ListCompaniesUseCase"""
        # Arrange
        mock_list_instance = Mock()
        mock_list_use_case.return_value = mock_list_instance
        
        expected_companies = [
            CompanyEntity(id=1, name="Company 1", api_token="token1"),
            CompanyEntity(id=2, name="Company 2", api_token="token2")
        ]
        mock_list_instance.execute.return_value = expected_companies
        
        # Act
        response = cast(Response, self.client.get("/api/companies/"))
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_list_use_case.assert_called_once()
        mock_list_instance.execute.assert_called_once()
        
        data = cast(list[dict[str, Any]], response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Company 1")
        self.assertEqual(data[1]["name"], "Company 2")
    
    @patch('core.app.providers.company.get_get_company_use_case')
    def test_company_get_detail_should_use_get_company_use_case(
        self,
        mock_get_use_case: Mock
    ):
        """Test that GET /api/companies/{id}/ uses GetCompanyUseCase"""
        # Arrange
        mock_get_instance = Mock()
        mock_get_use_case.return_value = mock_get_instance
        
        expected_company = CompanyEntity(
            id=1,
            name="Test Company",
            api_token="test-token"
        )
        mock_get_instance.execute.return_value = expected_company
        
        # Act
        response = cast(Response, self.client.get("/api/companies/1/"))
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_get_use_case.assert_called_once()
        mock_get_instance.execute.assert_called_once_with(1)
        
        data = cast(dict[str, Any], response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Test Company")
    
    @patch('core.app.providers.company.get_delete_company_use_case')
    def test_company_delete_should_use_delete_company_use_case(
        self,
        mock_delete_use_case: Mock
    ):
        """Test that DELETE /api/companies/{id}/ uses DeleteCompanyUseCase"""
        # Arrange
        mock_delete_instance = Mock()
        mock_delete_use_case.return_value = mock_delete_instance
        
        # Act
        response = cast(Response, self.client.delete("/api/companies/1/"))
        
        # Assert
        self.assertEqual(response.status_code, 204)
        mock_delete_use_case.assert_called_once()
        mock_delete_instance.execute.assert_called_once_with(1)
    
    @patch('core.app.providers.document.get_create_document_use_case')
    @patch('core.app.providers.document.get_list_documents_use_case')
    def test_document_post_should_use_create_document_use_case(
        self,
        mock_list_use_case: Mock,
        mock_create_use_case: Mock
    ):
        """Test that POST /api/documents/ uses CreateDocumentUseCase"""
        # Arrange
        mock_create_instance = Mock()
        mock_create_use_case.return_value = mock_create_instance
        
        expected_document = DocumentEntity(
            id=1,
            name="Test Document",
            company_id=1,
            signer_ids=[]
        )
        mock_create_instance.execute.return_value = expected_document
        
        # Act
        response = cast(Response, self.client.post(
            "/api/documents/",
            {"name": "Test Document", "company": 1},
            format="json"
        ))
        
        # Assert
        self.assertEqual(response.status_code, 201)
        mock_create_use_case.assert_called_once()
        mock_create_instance.execute.assert_called_once()
        
        # Verify the use case was called with correct entity
        call_args = mock_create_instance.execute.call_args[0][0]
        self.assertEqual(call_args.name, "Test Document")
        self.assertEqual(call_args.company_id, 1)
    
    @patch('core.app.providers.signer.get_create_signer_use_case')
    @patch('core.app.providers.signer.get_list_signers_use_case')
    def test_signer_post_should_use_create_signer_use_case(
        self,
        mock_list_use_case: Mock,
        mock_create_use_case: Mock
    ):
        """Test that POST /api/signers/ uses CreateSignerUseCase"""
        # Arrange
        mock_create_instance = Mock()
        mock_create_use_case.return_value = mock_create_instance
        
        expected_signer = SignerEntity(
            id=1,
            name="John Doe",
            email="john@example.com"
        )
        mock_create_instance.execute.return_value = expected_signer
        
        # Act
        response = cast(Response, self.client.post(
            "/api/signers/",
            {"name": "John Doe", "email": "john@example.com"},
            format="json"
        ))
        
        # Assert
        self.assertEqual(response.status_code, 201)
        mock_create_use_case.assert_called_once()
        mock_create_instance.execute.assert_called_once()
        
        # Verify the use case was called with correct entity
        call_args = mock_create_instance.execute.call_args[0][0]
        self.assertEqual(call_args.name, "John Doe")
        self.assertEqual(call_args.email, "john@example.com")


class ApiViewSetArchitectureTests(APITestCase):
    """Test that ViewSets are properly structured for Clean Architecture"""
    
    def test_company_viewset_should_not_use_model_viewset(self):
        """Ensure CompanyViewSet doesn't inherit from ModelViewSet"""
        from api.views.company import CompanyViewSet
        from rest_framework.viewsets import ModelViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            issubclass(CompanyViewSet, ModelViewSet),
            "CompanyViewSet should not inherit from ModelViewSet to avoid direct ORM access"
        )
    
    def test_document_viewset_should_not_use_model_viewset(self):
        """Ensure DocumentViewSet doesn't inherit from ModelViewSet"""
        from api.views.document import DocumentViewSet
        from rest_framework.viewsets import ModelViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            issubclass(DocumentViewSet, ModelViewSet),
            "DocumentViewSet should not inherit from ModelViewSet to avoid direct ORM access"
        )
    
    def test_signer_viewset_should_not_use_model_viewset(self):
        """Ensure SignerViewSet doesn't inherit from ModelViewSet"""
        from api.views.signer import SignerViewSet
        from rest_framework.viewsets import ModelViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            issubclass(SignerViewSet, ModelViewSet),
            "SignerViewSet should not inherit from ModelViewSet to avoid direct ORM access"
        )
    
    def test_company_viewset_should_not_have_queryset_attribute(self):
        """Ensure CompanyViewSet doesn't have a queryset attribute"""
        from api.views.company import CompanyViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            hasattr(CompanyViewSet, 'queryset'),
            "CompanyViewSet should not have queryset attribute to avoid direct ORM access"
        )
    
    def test_document_viewset_should_not_have_queryset_attribute(self):
        """Ensure DocumentViewSet doesn't have a queryset attribute"""
        from api.views.document import DocumentViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            hasattr(DocumentViewSet, 'queryset'),
            "DocumentViewSet should not have queryset attribute to avoid direct ORM access"
        )
    
    def test_signer_viewset_should_not_have_queryset_attribute(self):
        """Ensure SignerViewSet doesn't have a queryset attribute"""
        from api.views.signer import SignerViewSet
        
        # This test will fail initially and pass after refactoring
        self.assertFalse(
            hasattr(SignerViewSet, 'queryset'),
            "SignerViewSet should not have queryset attribute to avoid direct ORM access"
        )