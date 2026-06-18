from rest_framework.routers import DefaultRouter

from memos_cafe.mesas.api.views import MesaViewSet

router = DefaultRouter()
router.register("", MesaViewSet, basename="mesa")

urlpatterns = router.urls