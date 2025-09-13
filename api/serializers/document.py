from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    company = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    signers = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    status = serializers.CharField(max_length=50, required=False, allow_blank=True)
    token = serializers.CharField(max_length=255, read_only=True)
    open_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_by = serializers.CharField(max_length=150, required=False, allow_blank=True)
    external_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)

