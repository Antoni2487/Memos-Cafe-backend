from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from memos_cafe.ordenes.models import Orden
from memos_cafe.ordenes.services import DetalleOrdenService, OrdenService
from memos_cafe.ordenes.api.serializers import (
    DetalleOrdenWriteSerializer,
    MarcarImpresoSerializer,
    OrdenReadSerializer,
    OrdenWriteSerializer,
)
from memos_cafe.utils.permissions import EsAdmin, EsAdminOMesero, TodosAutenticados


class OrdenViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Gestión de órdenes.
    El ViewSet solo maneja HTTP — delega lógica a OrdenService.
    """

    def get_queryset(self):
        user = self.request.user
        # Mesero solo ve sus propias órdenes abiertas
        if user.groups.filter(name="mesero").exists():
            return Orden.objects.abiertas_por_usuario(user)
        # Cajero y admin ven todas las abiertas
        return Orden.objects.abiertas()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        if self.action in ["crear", "agregar_detalle", "eliminar_detalle"]:
            return [EsAdminOMesero()]
        return [EsAdmin()]

    def get_serializer_class(self):
        return OrdenReadSerializer

    @action(detail=False, methods=["post"], url_path="crear")
    def crear(self, request):
        """POST /api/ordenes/crear/ — crea una orden con sus ítems."""
        serializer = OrdenWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            orden = OrdenService.crear_orden(
                usuario=request.user,
                tipo_orden=serializer.validated_data["tipo_orden"],
                mesa=serializer.validated_data.get("mesa"),
                detalles=serializer.validated_data["detalles"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrdenReadSerializer(orden).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="anular", permission_classes=[EsAdmin])
    def anular(self, request, pk=None):
        """POST /api/ordenes/{id}/anular/ — solo admin."""
        orden = self.get_object()
        try:
            OrdenService.anular_orden(orden)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrdenReadSerializer(orden).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="detalles",
        permission_classes=[EsAdminOMesero],
    )
    def agregar_detalle(self, request, pk=None):
        """POST /api/ordenes/{id}/detalles/ — agrega un ítem."""
        orden = self.get_object()
        serializer = DetalleOrdenWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            DetalleOrdenService.agregar_detalle(
                orden=orden,
                **serializer.validated_data,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        orden.refresh_from_db()
        return Response(OrdenReadSerializer(orden).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"detalles/(?P<detalle_id>\d+)",
        permission_classes=[EsAdminOMesero],
    )
    def eliminar_detalle(self, request, pk=None, detalle_id=None):
        """DELETE /api/ordenes/{id}/detalles/{detalle_id}/"""
        orden = self.get_object()
        try:
            estaba_impreso = DetalleOrdenService.eliminar_detalle(
                orden=orden,
                detalle_id=int(detalle_id),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        orden.refresh_from_db()
        data = OrdenReadSerializer(orden).data
        data["item_eliminado_impreso"] = estaba_impreso
        return Response(data)

    @action(
        detail=True,
        methods=["post"],
        url_path="marcar-impreso",
        permission_classes=[EsAdminOMesero],
    )
    def marcar_impreso(self, request, pk=None):
        """POST /api/ordenes/{id}/marcar-impreso/ — marca ítems como enviados a cocina/barra."""
        orden = self.get_object()
        serializer = MarcarImpresoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DetalleOrdenService.marcar_impreso(orden, serializer.validated_data["detalle_ids"])
        orden.refresh_from_db()
        return Response(OrdenReadSerializer(orden).data)