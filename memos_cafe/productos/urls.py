from rest_framework.routers import DefaultRouter

from memos_cafe.productos.api.views import (
    CategoriaViewSet,
    ProductoViewSet,
    PromocionViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("", ProductoViewSet, basename="producto")
router.register("promociones", PromocionViewSet, basename="promocion")

urlpatterns = router.urls