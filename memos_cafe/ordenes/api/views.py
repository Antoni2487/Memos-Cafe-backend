from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from memos_cafe_backend.ordenes.models import DetalleOrden
from memos_cafe_backend.ordenes.models import Orden
from memos_cafe_backend.ordenes.api.serializers import DetalleOrdenWriteSerializer
from memos_cafe_backend.ordenes.api.serializers import OrdenReadSerializer
from memos_cafe_backend.ordenes.api.serializers import OrdenWriteSerializer
from memos_cafe_backend.utils.permissions import EsAdmin
from memos_cafe_backend.utils.permissions import EsAdminOMesero
from memos_cafe_backend.utils.permissions import TodosAutenticados


class OrdenViewSet(ModelViewSet):
    """
    list:    GET  /api/ordenes/              → todos los roles
    create:  POST /api/ordenes/              → admin o mesero
    retrieve:GET  /api/ordenes/{id}/         → todos los roles
    destroy: DELETE /api/ordenes/{id}/       → solo admin (anula)
    anular:  POST /api/ordenes/{id}/anular/  → solo admin
    """

    def get_queryset(self):
        user = self.request.user
        # El mesero solo ve sus propias órdenes abiertas
        if user.groups.filter(name="mesero").exists():
            return Orden.objects.filter(
                usuario=user,
                estado=Orden.Estado.ABIERTA,
            ).prefetch_related("detalles__producto", "detalles__promocion")
        # Cajero y admin ven todas las abiertas
        return Orden.objects.filter(
            estado=Orden.Estado.ABIERTA,
        ).prefetch_related("detalles__producto", "detalles__promocion")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        if self.action in ["create", "agregar_detalle", "eliminar_detalle"]:
            return [EsAdminOMesero()]
        return [EsAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            return OrdenWriteSerializer
        return OrdenReadSerializer

    def destroy(self, request, *args, **kwargs):
        """Anula la orden en vez de borrarla físicamente."""
        orden = self.get_object()
        try:
            orden.anular()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="anular")
    def anular(self, request, pk=None):
        """POST /api/ordenes/{id}/anular/"""
        orden = self.get_object()
        try:
            orden.anular()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrdenReadSerializer(orden).data)

    @action(detail=True, methods=["post"], url_path="detalles")
    def agregar_detalle(self, request, pk=None):
        """POST /api/ordenes/{id}/detalles/ — agrega un ítem a la orden."""
        orden = self.get_object()
        if orden.estado != Orden.Estado.ABIERTA:
            return Response(
                {"detail": "No se pueden agregar ítems a una orden cerrada o anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = DetalleOrdenWriteSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(orden=orden)
        return Response(OrdenReadSerializer(orden).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"detalles/(?P<detalle_id>\d+)")
    def eliminar_detalle(self, request, pk=None, detalle_id=None):
        """DELETE /api/ordenes/{id}/detalles/{detalle_id}/ — quita un ítem."""
        orden = self.get_object()
        try:
            detalle = orden.detalles.get(id=detalle_id)
        except DetalleOrden.DoesNotExist:
            return Response(
                {"detail": "Detalle no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        detalle.delete()
        orden.recalcular_total()
        return Response(OrdenReadSerializer(orden).data)