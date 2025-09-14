from rest_framework import viewsets
from core.orm.models import Document
from api.serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("company").prefetch_related("signers").order_by("-id")
    serializer_class = DocumentSerializer