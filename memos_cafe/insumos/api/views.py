from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from memos_cafe.insumos.models import RegistroInsumo, TipoInsumo
from memos_cafe.insumos.services import RegistroInsumoService, TipoInsumoService
from memos_cafe.insumos.api.serializers import (
    RegistroInsumoSerializer,
    RegistroInsumoWriteSerializer,
    TipoInsumoSerializer,
    TipoInsumoWriteSerializer,
)
from memos_cafe.utils.permissions import EsAdmin


class TipoInsumoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Catálogo de insumos con búsqueda, ordenación y paginación.
    Solo admin.
    """
    serializer_class = TipoInsumoSerializer
    permission_classes = [EsAdmin]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["nombre", "unidad"]
    ordering_fields = ["nombre", "stock_actual", "stock_minimo"]
    ordering = ["nombre"]

    def get_queryset(self):
        qs = TipoInsumo.objects.all()
        # Filtro opcional: ?stock_bajo=true
        stock_bajo = self.request.query_params.get("stock_bajo")
        if stock_bajo == "true":
            # Filtra insumos donde stock_actual <= stock_minimo
            from django.db.models import F
            qs = qs.filter(stock_actual__lte=F("stock_minimo"))
        return qs

    @action(detail=False, methods=["post"], url_path="crear")
    def crear(self, request):
        """POST /api/insumos/crear/"""
        serializer = TipoInsumoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            insumo = TipoInsumoService.crear(**serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TipoInsumoSerializer(insumo).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        """POST /api/insumos/{id}/desactivar/"""
        insumo = self.get_object()
        TipoInsumoService.desactivar(insumo)
        return Response(TipoInsumoSerializer(insumo).data)


class RegistroInsumoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Historial de compras de insumos.
    Inmutable — no hay update ni delete.
    Solo admin.
    """
    serializer_class = RegistroInsumoSerializer
    permission_classes = [EsAdmin]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["insumo__nombre", "proveedor"]
    ordering_fields = ["fecha", "costo_total", "cantidad"]
    ordering = ["-fecha"]

    def get_queryset(self):
        return RegistroInsumo.objects.select_related(
            "insumo", "usuario"
        ).all()

    @action(detail=False, methods=["post"], url_path="registrar")
    def registrar(self, request):
        """POST /api/insumos/registros/registrar/"""
        serializer = RegistroInsumoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registro = RegistroInsumoService.registrar_compra(
                usuario=request.user,
                **serializer.validated_data,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            RegistroInsumoSerializer(registro).data,
            status=status.HTTP_201_CREATED,
        )