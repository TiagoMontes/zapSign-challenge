from rest_framework import viewsets, permissions

from core.orm.models import Signer
from api.serializers import SignerSerializer


class SignerViewSet(viewsets.ModelViewSet):
    queryset = Signer.objects.all().order_by("-id")
    serializer_class = SignerSerializer
    permission_classes = [permissions.AllowAny]

