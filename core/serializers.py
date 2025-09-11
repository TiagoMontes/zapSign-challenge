from rest_framework import serializers
from .models import Company, Document, Signer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "api_token",
            "created_at",
            "last_updated_at",
        ]
        read_only_fields = ["id", "created_at", "last_updated_at"]


class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = [
            "id",
            "name",
            "email",
            "token",
            "status",
            "external_id",
        ]
        read_only_fields = ["id"]


class DocumentSerializer(serializers.ModelSerializer):
    signers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Signer.objects.all(), required=False
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "company",
            "open_id",
            "token",
            "name",
            "status",
            "created_by",
            "external_id",
            "signers",
            "created_at",
            "last_updated_at",
        ]
        read_only_fields = ["id", "created_at", "last_updated_at"]

