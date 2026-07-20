from __future__ import annotations

import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from memos_cafe.roles.models import PermisoRol
from memos_cafe.users.tests.factories import UserFactory
from memos_cafe.utils.permissions import modulo_requerido

pytestmark = pytest.mark.django_db

factory = APIRequestFactory()


def _request_de(user):
    request = factory.get("/")
    request.user = user
    return request


@pytest.fixture
def admin_user():
    grupo, _ = Group.objects.get_or_create(name="admin")
    user = UserFactory()
    user.groups.add(grupo)
    return user


@pytest.fixture
def cajero_user():
    grupo, _ = Group.objects.get_or_create(name="cajero")
    user = UserFactory()
    user.groups.add(grupo)
    return user


@pytest.fixture
def mesero_user():
    grupo, _ = Group.objects.get_or_create(name="mesero")
    user = UserFactory()
    user.groups.add(grupo)
    return user


class TestModuloHabilitado:
    def test_admin_siempre_pasa_aunque_no_haya_fila(self, admin_user):
        permiso = modulo_requerido("mesas")()
        assert permiso.has_permission(_request_de(admin_user), None) is True

    def test_admin_siempre_pasa_aunque_este_en_false(self, admin_user):
        PermisoRol.objects.update_or_create(
            modulo="mesas", rol="admin", defaults={"puede_acceder": False}
        )
        permiso = modulo_requerido("mesas")()
        assert permiso.has_permission(_request_de(admin_user), None) is True

    def test_rol_con_puede_acceder_true_pasa(self, mesero_user):
        PermisoRol.objects.update_or_create(
            modulo="ordenes", rol="mesero", defaults={"puede_acceder": True}
        )
        permiso = modulo_requerido("ordenes")()
        assert permiso.has_permission(_request_de(mesero_user), None) is True

    def test_rol_con_puede_acceder_false_bloquea(self, mesero_user):
        PermisoRol.objects.update_or_create(
            modulo="mesas", rol="mesero", defaults={"puede_acceder": False}
        )
        permiso = modulo_requerido("mesas")()
        assert permiso.has_permission(_request_de(mesero_user), None) is False

    def test_sin_fila_deniega_por_defecto(self, cajero_user):
        """Fail closed: si no existe el registro rol+modulo, no se asume acceso."""
        PermisoRol.objects.filter(modulo="mesas", rol="cajero").delete()
        permiso = modulo_requerido("mesas")()
        assert permiso.has_permission(_request_de(cajero_user), None) is False

    def test_usuario_sin_grupo_deniega(self):
        user = UserFactory()
        permiso = modulo_requerido("ordenes")()
        assert permiso.has_permission(_request_de(user), None) is False

    def test_usuario_no_autenticado_deniega(self):
        request = factory.get("/")
        request.user = type("Anon", (), {"is_authenticated": False})()
        permiso = modulo_requerido("mesas")()
        assert permiso.has_permission(request, None) is False

    def test_no_confunde_modulos_distintos(self, cajero_user):
        """puede_acceder=True en 'caja' no debe habilitar 'reportes'."""
        PermisoRol.objects.update_or_create(
            modulo="caja", rol="cajero", defaults={"puede_acceder": True}
        )
        PermisoRol.objects.update_or_create(
            modulo="reportes", rol="cajero", defaults={"puede_acceder": False}
        )
        assert modulo_requerido("caja")().has_permission(_request_de(cajero_user), None) is True
        assert modulo_requerido("reportes")().has_permission(_request_de(cajero_user), None) is False
