from rest_framework import serializers
from .company import CompanySerializer
from .signer import SignerSerializer


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    company = CompanySerializer(read_only=True)
    name = serializers.CharField(max_length=255)
    signers = SignerSerializer(many=True, read_only=True)
    status = serializers.CharField(max_length=50, required=False, allow_blank=True)
    token = serializers.CharField(max_length=255, read_only=True)
    open_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_by = serializers.CharField(max_length=150, required=False, allow_blank=True)
    external_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)

    # PDF processing fields
    pdf_url = serializers.URLField(read_only=True, allow_null=True)
    processing_status = serializers.CharField(max_length=20, read_only=True)
    checksum = serializers.CharField(max_length=64, read_only=True, allow_null=True)
    version_id = serializers.CharField(max_length=36, read_only=True, allow_null=True)

