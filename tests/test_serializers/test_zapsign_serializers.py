from typing import Any, Dict, cast
from rest_framework.exceptions import ValidationError
from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer


class TestZapSignSignerRequestSerializer:
    def test_validates_required_name_field(self):
        from api.serializers.zapsign_document import ZapSignSignerRequestSerializer

        serializer = ZapSignSignerRequestSerializer(data={})

        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_validates_with_minimal_data(self):
        from api.serializers.zapsign_document import ZapSignSignerRequestSerializer

        data = {"name": "John Doe"}
        serializer = ZapSignSignerRequestSerializer(data=data)

        assert serializer.is_valid()
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        assert validated_data["name"] == "John Doe"

    def test_validates_with_full_data(self):
        from api.serializers.zapsign_document import ZapSignSignerRequestSerializer

        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "auth_mode": "assinaturaTela",
            "send_automatic_email": True,
            "send_automatic_whatsapp": False,
            "order_group": None,
            "custom_message": "Please sign this document",
            "phone_country": "55",
            "phone_number": "11958039555",
            "lock_email": False,
            "blank_email": False,
            "hide_email": False,
            "lock_phone": False,
            "blank_phone": False,
            "hide_phone": False,
            "lock_name": False,
            "require_cpf": False,
            "cpf": "",
            "require_selfie_photo": True,
            "require_document_photo": True,
            "selfie_validation_type": "liveness-document-match",
            "selfie_photo_url": "",
            "document_photo_url": "",
            "document_verse_photo_url": "",
            "qualification": "",
            "external_id": "signer-123",
            "redirect_link": "",
        }

        serializer = ZapSignSignerRequestSerializer(data=data)

        assert serializer.is_valid()
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        assert validated_data["name"] == "John Doe"
        assert validated_data["email"] == "john@example.com"
        assert validated_data["require_selfie_photo"] is True
        assert validated_data["external_id"] == "signer-123"

    def test_validates_email_format(self):
        from api.serializers.zapsign_document import ZapSignSignerRequestSerializer

        data = {"name": "John Doe", "email": "invalid-email"}
        serializer = ZapSignSignerRequestSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors


class TestZapSignDocumentCreateSerializer:
    def test_validates_required_fields(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        serializer = ZapSignDocumentCreateSerializer(data={})

        assert not serializer.is_valid()
        assert "name" in serializer.errors
        assert "url_pdf" in serializer.errors
        assert "signers" in serializer.errors

    def test_validates_with_minimal_data(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "Test Document",
            "url_pdf": "https://example.com/document.pdf",
            "signers": [{"name": "John Doe"}],
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)

        assert serializer.is_valid()
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        assert validated_data["company_id"] == 1
        assert validated_data["name"] == "Test Document"
        assert validated_data["url_pdf"] == "https://example.com/document.pdf"
        assert len(validated_data["signers"]) == 1
        assert validated_data["signers"][0]["name"] == "John Doe"

    def test_validates_with_full_data(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "My PDF Contract",
            "url_pdf": "https://zapsign.s3.amazonaws.com/2022/1/pdf/sample.pdf",
            "external_id": "doc-123",
            "signers": [
                {"name": "My First API Signer PDF"},
                {
                    "name": "My Second API Signer PDF",
                    "email": "andre@zapsign.com.br",
                    "auth_mode": "assinaturaTela",
                    "send_automatic_email": True,
                    "send_automatic_whatsapp": False,
                    "order_group": None,
                    "custom_message": "",
                    "phone_country": "55",
                    "phone_number": "11958039555",
                    "lock_email": False,
                    "blank_email": False,
                    "hide_email": False,
                    "lock_phone": False,
                    "blank_phone": False,
                    "hide_phone": False,
                    "lock_name": False,
                    "require_cpf": False,
                    "cpf": "",
                    "require_selfie_photo": True,
                    "require_document_photo": True,
                    "selfie_validation_type": "liveness-document-match",
                    "selfie_photo_url": "",
                    "document_photo_url": "",
                    "document_verse_photo_url": "",
                    "qualification": "",
                    "external_id": "",
                    "redirect_link": "",
                },
            ],
            "lang": "pt-br",
            "disable_signer_emails": False,
            "brand_logo": "",
            "brand_primary_color": "",
            "brand_name": "",
            "folder_path": "/",
            "created_by": "",
            "date_limit_to_sign": None,
            "signature_order_active": False,
            "observers": ["test@observer.com"],
            "reminder_every_n_days": 0,
            "allow_refuse_signature": False,
            "disable_signers_get_original_file": False,
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)

        assert serializer.is_valid()
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        assert validated_data["company_id"] == 1
        assert validated_data["name"] == "My PDF Contract"
        assert validated_data["external_id"] == "doc-123"
        assert validated_data["lang"] == "pt-br"
        assert len(validated_data["signers"]) == 2
        assert validated_data["observers"] == ["test@observer.com"]

    def test_validates_url_pdf_format(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "Test Document",
            "url_pdf": "not-a-valid-url",
            "signers": [{"name": "John Doe"}],
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "url_pdf" in serializer.errors

    def test_validates_empty_signers_list(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "Test Document",
            "url_pdf": "https://example.com/document.pdf",
            "signers": [],
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)

        # Should be valid - empty signers list is allowed
        assert serializer.is_valid()

    def test_validates_invalid_signer_data(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "Test Document",
            "url_pdf": "https://example.com/document.pdf",
            "signers": [{"email": "john@example.com"}],  # Missing required name
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "signers" in serializer.errors

    def test_to_zapsign_request_conversion(self):
        from api.serializers.zapsign_document import ZapSignDocumentCreateSerializer

        data = {
            "company_id": 1,
            "name": "Test Document",
            "url_pdf": "https://example.com/document.pdf",
            "signers": [
                {"name": "John Doe", "email": "john@example.com"},
                {"name": "Jane Smith"},
            ],
            "external_id": "doc-456",
            "lang": "en",
        }

        serializer = ZapSignDocumentCreateSerializer(data=data)
        assert serializer.is_valid()

        # Type cast to access our custom method
        typed_serializer = cast(ZapSignDocumentCreateSerializer, serializer)
        zapsign_request = typed_serializer.to_zapsign_request()

        # Verify company_id is not in the ZapSign request
        assert not hasattr(zapsign_request, 'company_id')
        assert zapsign_request.name == "Test Document"
        assert zapsign_request.url_pdf == "https://example.com/document.pdf"
        assert zapsign_request.external_id == "doc-456"
        assert zapsign_request.lang == "en"
        assert len(zapsign_request.signers) == 2
        assert zapsign_request.signers[0].name == "John Doe"
        assert zapsign_request.signers[0].email == "john@example.com"
        assert zapsign_request.signers[1].name == "Jane Smith"


class TestZapSignDocumentResponseSerializer:
    def test_serializes_document_response(self):
        from api.serializers.zapsign_document import (
            ZapSignDocumentResponseSerializer,
            ZapSignSignerResponseSerializer,
        )
        from core.domain.value_objects.zapsign_response import (
            ZapSignDocumentResponse,
            ZapSignSignerResponse,
        )

        signer = ZapSignSignerResponse(
            token="signer-token-123",
            name="John Doe",
            status="new",
            email="john@example.com",
            external_id="signer-ext-123",
            sign_url="https://sandbox.app.zapsign.com.br/verificar/token",
        )

        document_response = ZapSignDocumentResponse(
            token="doc-token-123",
            name="Test Document",
            status="pending",
            open_id=42,
            external_id="doc-ext-123",
            created_by_email="user@example.com",
            signers=[signer],
        )

        serializer = ZapSignDocumentResponseSerializer(document_response)
        data = cast(Dict[str, Any], serializer.data)

        assert data["token"] == "doc-token-123"
        assert data["name"] == "Test Document"
        assert data["status"] == "pending"
        assert data["open_id"] == 42
        assert data["external_id"] == "doc-ext-123"
        assert data["created_by_email"] == "user@example.com"
        assert len(data["signers"]) == 1
        assert data["signers"][0]["token"] == "signer-token-123"
        assert data["signers"][0]["name"] == "John Doe"