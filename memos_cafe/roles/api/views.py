from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from memos_cafe.roles.models import PermisoRol
from memos_cafe.roles.api.serializers import PermisoRolSerializer
from memos_cafe.utils.permissions import EsAdmin


class PermisoRolViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = PermisoRolSerializer
    queryset         = PermisoRol.objects.all()
    lookup_field     = "pk"

    def get_permissions(self):
        return [EsAdmin()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
