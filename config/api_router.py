from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from memos_cafe.reportes.views import (
    DashboardView,
    ReporteCajaView,
    ReporteProductosView,
    ReporteVentasView,
)
from memos_cafe.users.api.views import CustomTokenObtainPairView

urlpatterns = [
    # Auth JWT
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Apps
    path("mesas/", include("memos_cafe.mesas.urls")),
    path("productos/", include("memos_cafe.productos.urls")),
    path("ordenes/", include("memos_cafe.ordenes.urls")),
    path("caja/", include("memos_cafe.caja.urls")),
    path("insumos/", include("memos_cafe.insumos.urls")),

    # Reportes y Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("reportes/ventas/", ReporteVentasView.as_view(), name="reporte-ventas"),
    path("reportes/productos/", ReporteProductosView.as_view(), name="reporte-productos"),
    path("reportes/caja/", ReporteCajaView.as_view(), name="reporte-caja"),
]