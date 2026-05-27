from rest_framework.routers import DefaultRouter

from memos_cafe.ordenes.api.views import OrdenViewSet

router = DefaultRouter()
router.register("", OrdenViewSet, basename="orden")

urlpatterns = router.urls