from rest_framework.routers import DefaultRouter

from memos_cafe.caja.api.views import (
    CajaViewSet,
    ComprobanteViewSet,
    MovimientoCajaViewSet,
    PagoViewSet,
)

router = DefaultRouter()
router.register("sesiones", CajaViewSet, basename="caja")
router.register("movimientos", MovimientoCajaViewSet, basename="movimiento-caja")
router.register("pagos", PagoViewSet, basename="pago")
router.register("comprobantes", ComprobanteViewSet, basename="comprobante")

urlpatterns = router.urls