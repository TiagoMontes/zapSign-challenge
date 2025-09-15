"""Serializers for ZapSign document creation API."""

from typing import List, Dict, Any, cast
from rest_framework import serializers
from core.domain.value_objects.zapsign_request import (
    ZapSignDocumentRequest,
    ZapSignSignerRequest,
)
from core.domain.value_objects.zapsign_response import (
    ZapSignDocumentResponse,
    ZapSignSignerResponse,
)


class ZapSignSignerRequestSerializer(serializers.Serializer):
    """Serializer for ZapSign signer request data."""

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    auth_mode = serializers.CharField(
        max_length=50, required=False, default="assinaturaTela"
    )
    send_automatic_email = serializers.BooleanField(required=False, default=False)
    send_automatic_whatsapp = serializers.BooleanField(required=False, default=False)
    order_group = serializers.IntegerField(required=False, allow_null=True)
    custom_message = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    phone_country = serializers.CharField(
        max_length=10, required=False, allow_blank=True, default=""
    )
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=""
    )
    lock_email = serializers.BooleanField(required=False, default=False)
    blank_email = serializers.BooleanField(required=False, default=False)
    hide_email = serializers.BooleanField(required=False, default=False)
    lock_phone = serializers.BooleanField(required=False, default=False)
    blank_phone = serializers.BooleanField(required=False, default=False)
    hide_phone = serializers.BooleanField(required=False, default=False)
    lock_name = serializers.BooleanField(required=False, default=False)
    require_cpf = serializers.BooleanField(required=False, default=False)
    cpf = serializers.CharField(
        max_length=14, required=False, allow_blank=True, default=""
    )
    require_selfie_photo = serializers.BooleanField(required=False, default=False)
    require_document_photo = serializers.BooleanField(required=False, default=False)
    selfie_validation_type = serializers.CharField(
        max_length=50, required=False, default="none"
    )
    selfie_photo_url = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    document_photo_url = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    document_verse_photo_url = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    qualification = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    external_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    redirect_link = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    def to_zapsign_signer_request(self) -> ZapSignSignerRequest:
        """Convert to ZapSign signer request value object."""
        if not hasattr(self, 'validated_data') or not self.validated_data:
            raise ValueError("Serializer must be validated before conversion")

        validated_data = cast(Dict[str, Any], self.validated_data)
        return ZapSignSignerRequest(
            name=validated_data["name"],
            email=validated_data.get("email", ""),
            auth_mode=validated_data.get("auth_mode", "assinaturaTela"),
            send_automatic_email=validated_data.get("send_automatic_email", False),
            send_automatic_whatsapp=validated_data.get("send_automatic_whatsapp", False),
            order_group=validated_data.get("order_group"),
            custom_message=validated_data.get("custom_message", ""),
            phone_country=validated_data.get("phone_country", ""),
            phone_number=validated_data.get("phone_number", ""),
            lock_email=validated_data.get("lock_email", False),
            blank_email=validated_data.get("blank_email", False),
            hide_email=validated_data.get("hide_email", False),
            lock_phone=validated_data.get("lock_phone", False),
            blank_phone=validated_data.get("blank_phone", False),
            hide_phone=validated_data.get("hide_phone", False),
            lock_name=validated_data.get("lock_name", False),
            require_cpf=validated_data.get("require_cpf", False),
            cpf=validated_data.get("cpf", ""),
            require_selfie_photo=validated_data.get("require_selfie_photo", False),
            require_document_photo=validated_data.get("require_document_photo", False),
            selfie_validation_type=validated_data.get("selfie_validation_type", "none"),
            selfie_photo_url=validated_data.get("selfie_photo_url", ""),
            document_photo_url=validated_data.get("document_photo_url", ""),
            document_verse_photo_url=validated_data.get("document_verse_photo_url", ""),
            qualification=validated_data.get("qualification", ""),
            external_id=validated_data.get("external_id", ""),
            redirect_link=validated_data.get("redirect_link", "")
        )


class ZapSignDocumentCreateSerializer(serializers.Serializer):
    """Serializer for ZapSign document creation request."""

    company_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    url_pdf = serializers.URLField()
    external_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    signers = ZapSignSignerRequestSerializer(many=True)
    lang = serializers.CharField(max_length=10, required=False, default="pt-br")
    disable_signer_emails = serializers.BooleanField(required=False, default=False)
    brand_logo = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    brand_primary_color = serializers.CharField(
        max_length=10, required=False, allow_blank=True, default=""
    )
    brand_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    folder_path = serializers.CharField(
        max_length=255, required=False, default="/"
    )
    created_by = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )
    date_limit_to_sign = serializers.DateTimeField(
        required=False, allow_null=True
    )
    signature_order_active = serializers.BooleanField(required=False, default=False)
    observers = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    reminder_every_n_days = serializers.IntegerField(required=False, default=0)
    allow_refuse_signature = serializers.BooleanField(required=False, default=False)
    disable_signers_get_original_file = serializers.BooleanField(
        required=False, default=False
    )

    def validate_signers(self, value):
        """Custom validation for signers."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Signers must be a list.")

        # Allow empty signers list
        return value

    def to_zapsign_request(self) -> ZapSignDocumentRequest:
        """Convert to ZapSign request value object."""
        if not hasattr(self, 'validated_data') or not self.validated_data:
            raise ValueError("Serializer must be validated before conversion")

        # Create a copy to avoid modifying the original
        validated_data = dict(cast(Dict[str, Any], self.validated_data))

        # Remove company_id as it's not part of ZapSign request
        validated_data.pop("company_id", None)

        # Convert nested signers
        signers_data = validated_data.pop("signers", [])
        signers = []
        for signer_data in signers_data:
            signer_serializer = ZapSignSignerRequestSerializer(data=signer_data)
            if signer_serializer.is_valid():
                # Type cast to access our custom method
                typed_serializer = cast(ZapSignSignerRequestSerializer, signer_serializer)
                signers.append(typed_serializer.to_zapsign_signer_request())
            else:
                raise serializers.ValidationError(f"Invalid signer data: {signer_serializer.errors}")

        validated_data["signers"] = signers

        return ZapSignDocumentRequest(**validated_data)


class ZapSignSignerResponseSerializer(serializers.Serializer):
    """Serializer for ZapSign signer response data."""

    token = serializers.CharField()
    name = serializers.CharField()
    status = serializers.CharField()
    email = serializers.CharField()
    external_id = serializers.CharField()
    sign_url = serializers.CharField()
    lock_name = serializers.BooleanField()
    lock_email = serializers.BooleanField()
    hide_email = serializers.BooleanField()
    blank_email = serializers.BooleanField()
    phone_country = serializers.CharField()
    phone_number = serializers.CharField()
    lock_phone = serializers.BooleanField()
    hide_phone = serializers.BooleanField()
    blank_phone = serializers.BooleanField()
    times_viewed = serializers.IntegerField()
    last_view_at = serializers.CharField(allow_null=True)
    signed_at = serializers.CharField(allow_null=True)
    auth_mode = serializers.CharField()
    qualification = serializers.CharField()
    require_selfie_photo = serializers.BooleanField()
    require_document_photo = serializers.BooleanField()
    geo_latitude = serializers.FloatField(allow_null=True)
    geo_longitude = serializers.FloatField(allow_null=True)
    redirect_link = serializers.CharField()


class ZapSignDocumentResponseSerializer(serializers.Serializer):
    """Serializer for ZapSign document response data."""

    token = serializers.CharField()
    name = serializers.CharField()
    status = serializers.CharField()
    open_id = serializers.IntegerField()
    external_id = serializers.CharField()
    created_by_email = serializers.CharField()
    sandbox = serializers.BooleanField()
    folder_path = serializers.CharField()
    folder_token = serializers.CharField(allow_null=True)
    rejected_reason = serializers.CharField(allow_null=True)
    lang = serializers.CharField()
    original_file = serializers.CharField()
    signed_file = serializers.CharField(allow_null=True)
    created_through = serializers.CharField()
    deleted = serializers.BooleanField()
    deleted_at = serializers.CharField(allow_null=True)
    signed_file_only_finished = serializers.BooleanField()
    disable_signer_emails = serializers.BooleanField()
    brand_logo = serializers.CharField()
    brand_primary_color = serializers.CharField()
    created_at = serializers.CharField()
    last_update_at = serializers.CharField()
    template = serializers.CharField(allow_null=True)
    signers = ZapSignSignerResponseSerializer(many=True)
    auto_reminder = serializers.IntegerField()
    signature_report = serializers.CharField(allow_null=True)
    tsa_country = serializers.CharField(allow_null=True)
    use_timestamp = serializers.BooleanField()