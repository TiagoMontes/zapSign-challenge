from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views import CompanyViewSet, DocumentViewSet, SignerViewSet
from api.views.zapsign_document import ZapSignDocumentViewSet

# Main router for existing endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"signers", SignerViewSet, basename="signer")

# V1 router for ZapSign integration
v1_router = DefaultRouter(trailing_slash=False)
v1_router.register(r"docs", ZapSignDocumentViewSet, basename="zapsign-document")

urlpatterns = [
    path("", include(router.urls)),
    path("v1/", include(v1_router.urls)),
]

