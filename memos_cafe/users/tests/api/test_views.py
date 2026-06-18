from __future__ import annotations

import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from memos_cafe.users.tests.factories import UserFactory


@pytest.fixture
def admin_group(db):
    return Group.objects.get_or_create(name="admin")[0]


@pytest.fixture
def cajero_group(db):
    return Group.objects.get_or_create(name="cajero")[0]


@pytest.fixture
def mesero_group(db):
    return Group.objects.get_or_create(name="mesero")[0]


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


# ── /api/users/ ──────────────────────────────────────────────────


class TestUserList:
    @pytest.mark.django_db
    def test_admin_puede_listar_usuarios(self, admin_client, admin_user):
        response = admin_client.get("/api/users/")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_cajero_no_puede_listar_usuarios(self, cajero_client):
        response = cajero_client.get("/api/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_anonimo_no_puede_listar_usuarios(self, api_client):
        response = api_client.get("/api/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── /api/users/me/ ───────────────────────────────────────────────


class TestUserMe:
    @pytest.mark.django_db
    def test_usuario_autenticado_obtiene_su_perfil(self, admin_client, admin_user):
        response = admin_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == admin_user.email

    @pytest.mark.django_db
    def test_cajero_obtiene_su_perfil(self, cajero_client, cajero_user):
        response = cajero_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == cajero_user.email

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_anonimo_no_puede_ver_perfil(self, api_client):
        response = api_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── POST /api/users/ ─────────────────────────────────────────────


class TestUserCreate:
    def test_admin_puede_crear_usuario(self, admin_client):
        response = admin_client.post("/api/users/", {
            "email": "nuevo@test.com",
            "password": "Nuevo1234!",
            "name": "Nuevo Usuario",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "nuevo@test.com"

    def test_cajero_no_puede_crear_usuario(self, cajero_client):
        response = cajero_client.post("/api/users/", {
            "email": "nuevo@test.com",
            "password": "Nuevo1234!",
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_crear_usuario_sin_email_falla(self, admin_client):
        response = admin_client.post("/api/users/", {
            "password": "Nuevo1234!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_crear_usuario_password_corto_falla(self, admin_client):
        response = admin_client.post("/api/users/", {
            "email": "corto@test.com",
            "password": "123",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── DELETE /api/users/{id}/ ──────────────────────────────────────


class TestUserDelete:
    def test_admin_puede_eliminar_otro_usuario(self, admin_client, db, cajero_group):
        otro = UserFactory.create()
        otro.groups.add(cajero_group)
        response = admin_client.delete(f"/api/users/{otro.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_no_puede_eliminarse_a_si_mismo(self, admin_client, admin_user):
        response = admin_client.delete(f"/api/users/{admin_user.pk}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "propia cuenta" in response.data["detail"]

    def test_cajero_no_puede_eliminar_usuario(self, cajero_client, db):
        otro = UserFactory.create()
        response = cajero_client.delete(f"/api/users/{otro.pk}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── POST /api/users/{id}/toggle-activo/ ──────────────────────────


class TestToggleActivo:
    def test_admin_puede_desactivar_usuario(self, admin_client, db, cajero_group):
        otro = UserFactory.create()
        otro.groups.add(cajero_group)
        assert otro.is_active is True
        response = admin_client.post(f"/api/users/{otro.pk}/toggle-activo/")
        assert response.status_code == status.HTTP_200_OK
        otro.refresh_from_db()
        assert otro.is_active is False

    def test_admin_no_puede_desactivarse_a_si_mismo(self, admin_client, admin_user):
        response = admin_client.post(f"/api/users/{admin_user.pk}/toggle-activo/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cajero_no_puede_toggle_activo(self, cajero_client, db):
        otro = UserFactory.create()
        response = cajero_client.post(f"/api/users/{otro.pk}/toggle-activo/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── POST /api/auth/login/ ────────────────────────────────────────


class TestLogin:
    @pytest.mark.django_db
    def test_login_exitoso(self, api_client, admin_user):
        response = api_client.post("/api/auth/login/", {
            "email": admin_user.email,
            "password": "Admin1234!",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    @pytest.mark.django_db
    def test_login_credenciales_invalidas(self, api_client):
        response = api_client.post("/api/auth/login/", {
            "email": "noexiste@test.com",
            "password": "wrongpassword",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
