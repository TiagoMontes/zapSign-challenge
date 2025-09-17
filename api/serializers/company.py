from rest_framework import serializers


class CompanySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    api_token = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)


class CompanyWithDocumentsSerializer(serializers.Serializer):
    """Company serializer that includes associated documents."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    api_token = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)
    last_updated_at = serializers.DateTimeField(read_only=True)

    # Import inline to avoid circular import
    def get_documents(self, obj):
        from .document import DocumentBasicSerializer
        # obj is expected to have a 'documents' attribute
        if hasattr(obj, 'documents'):
            return DocumentBasicSerializer(obj.documents, many=True).data
        return []

    documents = serializers.SerializerMethodField(method_name='get_documents')

