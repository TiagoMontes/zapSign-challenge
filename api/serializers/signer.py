from rest_framework import serializers

from core.orm.models import Signer


class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = ["id", "name", "email", "token", "status", "external_id"]
        read_only_fields = ["id", "token", "status"]

