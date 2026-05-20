
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from memos_cafe.insumos.models import RegistroInsumo
from memos_cafe.insumos.models import TipoInsumo
from memos_cafe.insumos.api.serializers import RegistroInsumoSerializer
from memos_cafe.insumos.api.serializers import TipoInsumoSerializer
from memos_cafe.utils.permissions import EsAdmin


class TipoInsumoViewSet(ModelViewSet):
    """CRUD completo — solo admin."""
    serializer_class = TipoInsumoSerializer
    permission_classes = [EsAdmin]
    queryset = TipoInsumo.objects.filter(activo=True).order_by("nombre")


class RegistroInsumoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    list/retrieve → solo admin
    create        → solo admin
    No hay update ni delete — los registros de compras son inmutables.
    """
    serializer_class = RegistroInsumoSerializer
    permission_classes = [EsAdmin]
    queryset = RegistroInsumo.objects.select_related("insumo", "usuario").all()