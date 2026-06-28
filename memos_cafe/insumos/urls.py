
from rest_framework.routers import DefaultRouter
from memos_cafe.insumos.api.views import RegistroInsumoViewSet, TipoInsumoViewSet

router = DefaultRouter()
router.register("registros", RegistroInsumoViewSet, basename="registro-insumo")
router.register("", TipoInsumoViewSet, basename="tipo-insumo")

urlpatterns = router.urls