from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from memos_cafe.mesas.models import Mesa
from memos_cafe.mesas.services import MesaService
from memos_cafe.mesas.api.serializers import MesaEstadoSerializer
from memos_cafe.mesas.api.serializers import MesaSerializer
from memos_cafe.utils.permissions import EsAdmin
from memos_cafe.utils.permissions import EsAdminOMesero
from memos_cafe.utils.permissions import TodosAutenticados


class MesaViewSet(ModelViewSet):
    """
    list:   GET  /api/mesas/          -> todos los roles
    create: POST /api/mesas/          -> solo admin
    update: PUT  /api/mesas/{id}/     -> solo admin
    destroy:DELETE /api/mesas/{id}/   -> solo admin (da de baja)
    estado: PATCH /api/mesas/{id}/estado/ -> admin o mesero
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

    def perform_create(self, serializer):
        try:
            mesa = MesaService.crear(
                numero=serializer.validated_data["numero"],
                capacidad=serializer.validated_data["capacidad"],
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})
        serializer.instance = mesa

    def perform_update(self, serializer):
        try:
            MesaService.actualizar(
                serializer.instance,
                numero=serializer.validated_data.get("numero"),
                capacidad=serializer.validated_data.get("capacidad"),
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

    def destroy(self, request, *args, **kwargs):
        """En vez de borrar fisicamente, da de baja la mesa."""
        mesa = self.get_object()
        try:
            MesaService.dar_de_baja(mesa)
        except ValueError as e:
            raise ValidationError({"detail": str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="estado")
    def estado(self, request, pk=None):
        mesa = self.get_object()
        serializer = MesaEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nuevo_estado = serializer.validated_data["estado"]

        try:
            MesaService.cambiar_estado(mesa, nuevo_estado)
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(MesaSerializer(mesa).data)
