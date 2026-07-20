from __future__ import annotations

import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from memos_cafe.users.tests.factories import UserFactory
from memos_cafe.roles.models import PermisoRol


@pytest.fixture
def admin_group(db):
    return Group.objects.get_or_create(name="admin")[0]


@pytest.fixture
def cajero_group(db):
    return Group.objects.get_or_create(name="cajero")[0]


@pytest.fixture
def admin_user(db, admin_group):
    user = UserFactory.create(password="Admin1234!")
    user.groups.add(admin_group)
    return user


@pytest.fixture
def cajero_user(db, cajero_group):
    user = UserFactory.create(password="Cajero1234!")
    user.groups.add(cajero_group)
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def cajero_client(api_client, cajero_user):
    api_client.force_authenticate(user=cajero_user)
    return api_client


@pytest.fixture
def permiso(db):
    # update_or_create: la migracion 0002_seed_permisos ya siembra las 24
    # combinaciones modulo x rol, asi que un .create() aca chocaria con
    # unique_together.
    permiso, _ = PermisoRol.objects.update_or_create(
        modulo="productos",
        rol="cajero",
        defaults={"puede_acceder": False},
    )
    return permiso


# ── GET /api/roles/permisos/ ─────────────────────────────────────


class TestPermisoRolList:
    @pytest.mark.django_db
    def test_admin_puede_listar_permisos(self, admin_client, permiso):
        response = admin_client.get("/api/roles/permisos/")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_cajero_puede_listar_permisos(self, cajero_client):
        """Cualquier autenticado necesita leer la tabla completa para poder
        calcular sus propios permisos en el frontend (Sidebar/rutas).
        Solo la edicion (PATCH) sigue siendo exclusiva de admin."""
        response = cajero_client.get("/api/roles/permisos/")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_anonimo_no_puede_listar_permisos(self, api_client):
        response = api_client.get("/api/roles/permisos/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_respuesta_tiene_campos_correctos(self, admin_client, permiso):
        response = admin_client.get("/api/roles/permisos/")
        # Sin paginacion (pagination_class = None): la respuesta es una
        # lista plana, no un dict con "results".
        data = response.data
        assert len(data) > 0
        item = data[0]
        assert "id" in item
        assert "modulo" in item
        assert "modulo_label" in item
        assert "rol" in item
        assert "rol_label" in item
        assert "puede_acceder" in item

    @pytest.mark.django_db
    def test_lista_no_esta_paginada_devuelve_todas_las_filas(self, admin_client, permiso):
        """Regresion: con paginacion default (20/pagina) esta tabla de 24
        filas perdia 'usuarios' y parte de 'reportes' en silencio."""
        response = admin_client.get("/api/roles/permisos/")
        assert isinstance(response.data, list)
        assert len(response.data) >= 24


# ── PATCH /api/roles/permisos/{id}/ ─────────────────────────────


class TestPermisoRolUpdate:
    @pytest.mark.django_db
    def test_admin_puede_actualizar_permiso(self, admin_client, permiso):
        assert permiso.puede_acceder is False
        response = admin_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"puede_acceder": True},
        )
        assert response.status_code == status.HTTP_200_OK
        permiso.refresh_from_db()
        assert permiso.puede_acceder is True

    @pytest.mark.django_db
    def test_admin_puede_desactivar_permiso(self, admin_client, permiso):
        permiso.puede_acceder = True
        permiso.save()
        response = admin_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"puede_acceder": False},
        )
        assert response.status_code == status.HTTP_200_OK
        permiso.refresh_from_db()
        assert permiso.puede_acceder is False

    @pytest.mark.django_db
    def test_cajero_no_puede_actualizar_permiso(self, cajero_client, permiso):
        response = cajero_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"puede_acceder": True},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_anonimo_no_puede_actualizar_permiso(self, api_client, permiso):
        response = api_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"puede_acceder": True},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_no_se_puede_cambiar_modulo(self, admin_client, permiso):
        response = admin_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"modulo": "caja", "puede_acceder": True},
        )
        assert response.status_code == status.HTTP_200_OK
        permiso.refresh_from_db()
        assert permiso.modulo == "productos"

    @pytest.mark.django_db
    def test_no_se_puede_cambiar_rol(self, admin_client, permiso):
        response = admin_client.patch(
            f"/api/roles/permisos/{permiso.pk}/",
            {"rol": "admin", "puede_acceder": True},
        )
        assert response.status_code == status.HTTP_200_OK
        permiso.refresh_from_db()
        assert permiso.rol == "cajero"


# ── Modelo PermisoRol ────────────────────────────────────────────


class TestPermisoRolModel:
    @pytest.mark.django_db
    def test_str_activo(self, db):
        p, _ = PermisoRol.objects.update_or_create(
            modulo="caja", rol="admin", defaults={"puede_acceder": True}
        )
        assert "admin" in str(p)
        assert "caja" in str(p)
        assert "✅" in str(p)

    @pytest.mark.django_db
    def test_str_inactivo(self, db):
        p, _ = PermisoRol.objects.update_or_create(
            modulo="reportes", rol="mesero", defaults={"puede_acceder": False}
        )
        assert "❌" in str(p)

    @pytest.mark.django_db
    def test_unique_together(self, db):
        PermisoRol.objects.filter(modulo="mesas", rol="cajero").delete()
        PermisoRol.objects.create(
            modulo="mesas", rol="cajero", puede_acceder=True
        )
        with pytest.raises(Exception):
            PermisoRol.objects.create(
                modulo="mesas", rol="cajero", puede_acceder=False
            )
