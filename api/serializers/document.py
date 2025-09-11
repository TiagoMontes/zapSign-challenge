from rest_framework import serializers

from core.orm.models import Document, Signer


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
        read_only_fields = ["id", "open_id", "token", "created_at", "last_updated_at"]

