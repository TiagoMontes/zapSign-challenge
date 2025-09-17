from rest_framework import serializers
from .company import CompanySerializer
from .signer import SignerSerializer


class DocumentBasicSerializer(serializers.Serializer):
    """Minimal document serializer with only basic fields for company responses."""
    id = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=50, required=False, allow_blank=True)


class DocumentSimpleSerializer(serializers.Serializer):
    """Simplified document serializer without company info to avoid circular references."""
    id = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(read_only=True)
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
    url_pdf = serializers.URLField(read_only=True, allow_null=True)
    processing_status = serializers.CharField(max_length=20, read_only=True)
    checksum = serializers.CharField(max_length=64, read_only=True, allow_null=True)
    version_id = serializers.CharField(max_length=36, read_only=True, allow_null=True)


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    signers = SignerSerializer(many=True, read_only=True)
    status = serializers.CharField(max_length=50, required=False, allow_blank=True)
    token = serializers.CharField(max_length=255, read_only=True)
    open_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_by = serializers.CharField(max_length=150, required=False, allow_blank=True)
    external_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)

    def get_company(self, obj):
        """Get company data for the document."""
        # Check if company data was already provided on the entity
        if hasattr(obj, 'company') and obj.company is not None:
            return CompanySerializer(obj.company).data

        # If not available on entity, we'll return None for now
        # In a complete implementation, this could fetch from a repository
        return None

    company = serializers.SerializerMethodField(method_name='get_company')

    # PDF processing fields
    url_pdf = serializers.URLField(read_only=True, allow_null=True)
    processing_status = serializers.CharField(max_length=20, read_only=True)
    checksum = serializers.CharField(max_length=64, read_only=True, allow_null=True)
    version_id = serializers.CharField(max_length=36, read_only=True, allow_null=True)

