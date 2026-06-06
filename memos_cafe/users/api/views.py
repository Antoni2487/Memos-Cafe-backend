from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from memos_cafe.users.models import User
from memos_cafe.users.api.serializers import CustomTokenObtainPairSerializer
from memos_cafe.users.api.serializers import UserSerializer
from memos_cafe.utils.permissions import EsAdmin, TodosAutenticados


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_permissions(self):
        if self.action in ["create", "destroy", "list", "update", "partial_update", "toggle_activo"]:
            return [EsAdmin()]
        return [TodosAutenticados()]

    def get_queryset(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return User.objects.none()
        if self.request.user.groups.filter(name="admin").exists():
            return User.objects.prefetch_related("groups").all()
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        group_name = request.data.get("group_name")
        if group_name is not None:
            instance.groups.clear()
            if group_name:
                try:
                    instance.groups.add(Group.objects.get(name=group_name))
                except Group.DoesNotExist:
                    pass

        instance.refresh_from_db()
        return Response(self.get_serializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "No puedes eliminar tu propia cuenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="toggle-activo")
    def toggle_activo(self, request, pk=None):
        """POST /api/users/{id}/toggle-activo/ — activa o desactiva un usuario."""
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "No puedes desactivar tu propia cuenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = not instance.is_active
        instance.save(update_fields=["is_active"])
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """GET /api/users/me/ — perfil del usuario autenticado."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
