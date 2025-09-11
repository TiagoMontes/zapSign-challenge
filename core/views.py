from rest_framework import viewsets
from .models import Company, Document, Signer
from .serializers import CompanySerializer, DocumentSerializer, SignerSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-id")
    serializer_class = CompanySerializer


class SignerViewSet(viewsets.ModelViewSet):
    queryset = Signer.objects.all().order_by("-id")
    serializer_class = SignerSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("company").prefetch_related("signers").order_by("-id")
    serializer_class = DocumentSerializer

