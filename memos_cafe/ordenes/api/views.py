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

    Permisos:
      list / retrieve      → todos los autenticados
      crear / detalles     → admin o mesero
      anular               → solo admin
    """

    def get_queryset(self):
        user = self.request.user
        qs = Orden.objects.con_detalles()

        # Mesero: solo sus órdenes abiertas
        if user.groups.filter(name="mesero").exists():
            return qs.filter(estado=Orden.Estado.ABIERTA, usuario=user)

        # Cajero y admin: todas las abiertas + cerradas del día de hoy
        # (necesario para historial de cobros y reportes de turno)
        from django.utils import timezone
        hoy = timezone.localdate()
        return qs.filter(fecha_creacion__date=hoy)

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
        data = serializer.validated_data
        try:
            orden = OrdenService.crear_orden(
                usuario=request.user,
                tipo_orden=data["tipo_orden"],
                mesa=data.get("mesa"),
                detalles=data["detalles"],
                cliente_nombre=data.get("cliente_nombre", ""),
                cliente_telefono=data.get("cliente_telefono", ""),
                direccion_entrega=data.get("direccion_entrega", ""),
                plataforma_delivery=data.get("plataforma_delivery") or "",
                plataforma_otra=data.get("plataforma_otra", ""),
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
        orden.refresh_from_db()  # Fix 5: asegurar estado actualizado antes de serializar
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
            DetalleOrdenService.agregar_detalle(orden=orden, **serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        orden.refresh_from_db()
        return Response(OrdenReadSerializer(orden).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        url_path="detalles/(?P<detalle_id>[0-9]+)",
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
