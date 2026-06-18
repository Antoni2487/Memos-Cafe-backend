from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    """Solo usuarios del grupo 'admin'."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="admin").exists()
        )


class EsCajero(BasePermission):
    """Solo usuarios del grupo 'cajero'."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="cajero").exists()
        )


class EsMesero(BasePermission):
    """Solo usuarios del grupo 'mesero'."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="mesero").exists()
        )


class EsAdminOCajero(BasePermission):
    """Admin o cajero."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name__in=["admin", "cajero"]).exists()
        )


class EsAdminOMesero(BasePermission):
    """Admin o mesero."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name__in=["admin", "mesero"]).exists()
        )


class TodosAutenticados(BasePermission):
    """Cualquier usuario autenticado (los 3 roles)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated