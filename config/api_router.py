from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from memos_cafe_backend.caja.api.views import CajaViewSet
from memos_cafe_backend.caja.api.views import ComprobanteViewSet
from memos_cafe_backend.caja.api.views import MovimientoCajaViewSet
from memos_cafe_backend.caja.api.views import PagoViewSet
from memos_cafe_backend.insumos.api.views import RegistroInsumoViewSet
from memos_cafe_backend.insumos.api.views import TipoInsumoViewSet
from memos_cafe_backend.mesas.api.views import MesaViewSet
from memos_cafe_backend.ordenes.api.views import OrdenViewSet
from memos_cafe_backend.productos.api.views import CategoriaViewSet
from memos_cafe_backend.productos.api.views import ProductoViewSet
from memos_cafe_backend.productos.api.views import PromocionViewSet
from memos_cafe_backend.reportes.views import ReporteCajaView
from memos_cafe_backend.reportes.views import ReporteProductosView
from memos_cafe_backend.reportes.views import ReporteVentasView

router = DefaultRouter()

# Productos
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("productos", ProductoViewSet, basename="producto")
router.register("promociones", PromocionViewSet, basename="promocion")

# Mesas
router.register("mesas", MesaViewSet, basename="mesa")

# Órdenes
router.register("ordenes", OrdenViewSet, basename="orden")

# Caja
router.register("caja", CajaViewSet, basename="caja")
router.register("movimientos", MovimientoCajaViewSet, basename="movimiento")
router.register("pagos", PagoViewSet, basename="pago")
router.register("comprobantes", ComprobanteViewSet, basename="comprobante")

# Insumos
router.register("insumos/tipos", TipoInsumoViewSet, basename="tipo-insumo")
router.register("insumos/registros", RegistroInsumoViewSet, basename="registro-insumo")

# Auth JWT
urlpatterns = router.urls + [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Reportes
    path("reportes/ventas/", ReporteVentasView.as_view(), name="reporte-ventas"),
    path("reportes/productos/", ReporteProductosView.as_view(), name="reporte-productos"),
    path("reportes/caja/", ReporteCajaView.as_view(), name="reporte-caja"),
]