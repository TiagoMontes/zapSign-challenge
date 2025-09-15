from django.test import TestCase
from datetime import datetime
from typing import List, Optional


class TestZapSignDocumentRequest(TestCase):
    def test_creates_document_request_with_required_fields(self):
        from core.domain.value_objects.zapsign_request import (
            ZapSignDocumentRequest,
            ZapSignSignerRequest,
        )

        signer = ZapSignSignerRequest(name="John Doe")
        request = ZapSignDocumentRequest(
            name="My PDF Contract",
            url_pdf="https://example.com/document.pdf",
            signers=[signer],
        )

        assert request.name == "My PDF Contract"
        assert request.url_pdf == "https://example.com/document.pdf"
        assert len(request.signers) == 1
        assert request.signers[0].name == "John Doe"

    def test_creates_document_request_with_all_fields(self):
        from core.domain.value_objects.zapsign_request import (
            ZapSignDocumentRequest,
            ZapSignSignerRequest,
        )

        signer1 = ZapSignSignerRequest(name="John Doe")
        signer2 = ZapSignSignerRequest(
            name="Jane Smith",
            email="jane@example.com",
            auth_mode="assinaturaTela",
            send_automatic_email=True,
            send_automatic_whatsapp=False,
            phone_country="55",
            phone_number="11958039555",
            lock_email=False,
            blank_email=False,
            hide_email=False,
            lock_phone=False,
            blank_phone=False,
            hide_phone=False,
            lock_name=False,
            require_cpf=False,
            cpf="",
            require_selfie_photo=True,
            require_document_photo=True,
            selfie_validation_type="liveness-document-match",
            qualification="",
            external_id="ext-123",
            redirect_link="",
        )

        request = ZapSignDocumentRequest(
            name="My PDF Contract",
            url_pdf="https://example.com/document.pdf",
            external_id="doc-123",
            signers=[signer1, signer2],
            lang="pt-br",
            disable_signer_emails=False,
            brand_logo="",
            brand_primary_color="",
            brand_name="",
            folder_path="/",
            created_by="user@example.com",
            date_limit_to_sign=None,
            signature_order_active=False,
            observers=["observer@example.com"],
            reminder_every_n_days=0,
            allow_refuse_signature=False,
            disable_signers_get_original_file=False,
        )

        assert request.name == "My PDF Contract"
        assert request.external_id == "doc-123"
        assert len(request.signers) == 2
        assert request.signers[1].email == "jane@example.com"
        assert request.signers[1].require_selfie_photo is True
        assert request.lang == "pt-br"
        assert request.observers == ["observer@example.com"]

    def test_converts_document_request_to_dict(self):
        from core.domain.value_objects.zapsign_request import (
            ZapSignDocumentRequest,
            ZapSignSignerRequest,
        )

        signer = ZapSignSignerRequest(
            name="John Doe", email="john@example.com", external_id="signer-123"
        )
        request = ZapSignDocumentRequest(
            name="Test Document",
            url_pdf="https://example.com/doc.pdf",
            signers=[signer],
            external_id="doc-456",
        )

        data = request.to_dict()

        assert data["name"] == "Test Document"
        assert data["url_pdf"] == "https://example.com/doc.pdf"
        assert data["external_id"] == "doc-456"
        assert len(data["signers"]) == 1
        assert data["signers"][0]["name"] == "John Doe"
        assert data["signers"][0]["email"] == "john@example.com"


class TestZapSignDocumentResponse(TestCase):
    def test_creates_document_response_from_api_data(self):
        from core.domain.value_objects.zapsign_response import (
            ZapSignDocumentResponse,
            ZapSignSignerResponse,
        )

        api_response = {
            "sandbox": False,
            "external_id": "doc-123",
            "open_id": 2,
            "token": "934f3d4b-eece-43bc-b4d1-04599ad2f9aa",
            "name": "My PDF Contract",
            "status": "pending",
            "created_by": {"email": "user@example.com"},
            "signers": [
                {
                    "external_id": "",
                    "sign_url": "https://sandbox.app.zapsign.com.br/verificar/adb099fc",
                    "token": "adb099fc-9f2f-4774-a263-de1aea884f75",
                    "status": "new",
                    "name": "John Doe",
                    "email": "",
                },
                {
                    "external_id": "signer-456",
                    "sign_url": "https://sandbox.app.zapsign.com.br/verificar/d7128112",
                    "token": "d7128112-4fc2-4347-8b66-138b9cb4cfc7",
                    "status": "new",
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                },
            ],
        }

        response = ZapSignDocumentResponse.from_api_response(api_response)

        assert response.external_id == "doc-123"
        assert response.open_id == 2
        assert response.token == "934f3d4b-eece-43bc-b4d1-04599ad2f9aa"
        assert response.name == "My PDF Contract"
        assert response.status == "pending"
        assert response.created_by_email == "user@example.com"
        assert len(response.signers) == 2

        signer1 = response.signers[0]
        assert signer1.token == "adb099fc-9f2f-4774-a263-de1aea884f75"
        assert signer1.name == "John Doe"
        assert signer1.status == "new"
        assert signer1.email == ""

        signer2 = response.signers[1]
        assert signer2.external_id == "signer-456"
        assert signer2.name == "Jane Smith"
        assert signer2.email == "jane@example.com"

    def test_handles_missing_optional_fields_in_response(self):
        from core.domain.value_objects.zapsign_response import ZapSignDocumentResponse

        api_response = {
            "external_id": None,
            "open_id": 1,
            "token": "test-token",
            "name": "Test Doc",
            "status": "pending",
            "created_by": {"email": "test@example.com"},
            "signers": [],
        }

        response = ZapSignDocumentResponse.from_api_response(api_response)

        assert response.external_id == ""
        assert response.open_id == 1
        assert response.token == "test-token"
        assert response.name == "Test Doc"
        assert response.status == "pending"
        assert len(response.signers) == 0