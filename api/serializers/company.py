from rest_framework import serializers

from core.orm.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "api_token", "created_at", "last_updated_at"]
        read_only_fields = ["id", "created_at", "last_updated_at"]

