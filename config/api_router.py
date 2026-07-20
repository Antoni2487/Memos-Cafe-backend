from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from memos_cafe.reportes.views import (
    AlertasView,
    DashboardView,
    HealthCheckView,
    ReporteCajaView,
    ReporteOrdenesExportView,
    ReporteOrdenesView,
    ReporteProductosView,
    ReporteVentasView,
    ReporteVentasExportView,
    ReporteCajaExportView,
    ReporteProductosExportView,
)
from memos_cafe.users.api.views import CustomTokenObtainPairView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Auth JWT
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),

    # Monitoreo
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Users
    path("alertas/", AlertasView.as_view(), name="alertas"),
    path("", include(router.urls)),
    path("roles/", include("memos_cafe.roles.urls")),

    # Apps
    path("mesas/", include("memos_cafe.mesas.urls")),
    path("productos/", include("memos_cafe.productos.urls")),
    path("ordenes/", include("memos_cafe.ordenes.urls")),
    path("caja/", include("memos_cafe.caja.urls")),
    path("insumos/", include("memos_cafe.insumos.urls")),

    # Reportes y Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("reportes/ventas/", ReporteVentasView.as_view(), name="reporte-ventas"),
    path("reportes/ventas/export/", ReporteVentasExportView.as_view(), name="reporte-ventas-export"),
    path("reportes/productos/export/", ReporteProductosExportView.as_view(), name="reporte-productos-export"),
    path("reportes/productos/", ReporteProductosView.as_view(), name="reporte-productos"),
    path("reportes/caja/export/", ReporteCajaExportView.as_view(), name="reporte-caja-export"),
    path("reportes/caja/", ReporteCajaView.as_view(), name="reporte-caja"),
    path("reportes/ordenes/", ReporteOrdenesView.as_view(), name="reporte-ordenes"),
    path("reportes/ordenes/export/", ReporteOrdenesExportView.as_view(), name="reporte-ordenes-export"),
]

