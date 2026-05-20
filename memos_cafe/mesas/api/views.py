from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from memos_cafe.mesas.models import Mesa
from memos_cafe.mesas.api.serializers import MesaEstadoSerializer
from memos_cafe.mesas.api.serializers import MesaSerializer
from memos_cafe.utils.permissions import EsAdmin
from memos_cafe.utils.permissions import EsAdminOMesero
from memos_cafe.utils.permissions import TodosAutenticados


class MesaViewSet(ModelViewSet):
    """
    list:   GET  /api/mesas/          → todos los roles
    create: POST /api/mesas/          → solo admin
    update: PUT  /api/mesas/{id}/     → solo admin
    destroy:DELETE /api/mesas/{id}/   → solo admin (da de baja)
    estado: PATCH /api/mesas/{id}/estado/ → admin o mesero
    """
    queryset = Mesa.objects.filter(activo=True).order_by("numero")
    serializer_class = MesaSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        if self.action == "estado":
            return [EsAdminOMesero()]
        return [EsAdmin()]

    def get_serializer_class(self):
        if self.action == "estado":
            return MesaEstadoSerializer
        return MesaSerializer

    def destroy(self, request, *args, **kwargs):
        """En vez de borrar físicamente, da de baja la mesa."""
        mesa = self.get_object()
        mesa.dar_de_baja()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="estado")
    def estado(self, request, pk=None):
        """PATCH /api/mesas/{id}/estado/ — cambia el estado de la mesa."""
        mesa = self.get_object()
        serializer = MesaEstadoSerializer(mesa, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MesaSerializer(mesa).data)