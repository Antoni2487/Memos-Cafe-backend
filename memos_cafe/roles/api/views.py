from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from memos_cafe.roles.models import PermisoRol
from memos_cafe.roles.api.serializers import PermisoRolSerializer
from memos_cafe.utils.permissions import EsAdmin, TodosAutenticados


class PermisoRolViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = PermisoRolSerializer
    queryset         = PermisoRol.objects.all()
    lookup_field     = "pk"
    # Tabla de referencia pequeña y acotada (rol x modulo): sin paginacion,
    # o tanto la grilla de admin como el frontend (que necesita la lista
    # completa para calcular sus propios permisos) pierden filas en
    # silencio apenas se superan los ~20 registros por pagina por defecto.
    pagination_class = None

    def get_permissions(self):
        # list: cualquier autenticado necesita leer su propio modulo x rol
        # para decidir que puede ver/hacer en el frontend. Editar sigue
        # siendo exclusivo de admin.
        if self.action == "list":
            return [TodosAutenticados()]
        return [EsAdmin()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
