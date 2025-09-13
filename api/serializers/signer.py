from rest_framework import serializers


class SignerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    token = serializers.CharField(max_length=255, read_only=True)
    status = serializers.CharField(max_length=50, required=False, allow_blank=True)
    external_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)

