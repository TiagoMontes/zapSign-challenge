from rest_framework import viewsets, permissions

from core.orm.models import Company
from api.serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-id")
    serializer_class = CompanySerializer
    permission_classes = [permissions.AllowAny]

