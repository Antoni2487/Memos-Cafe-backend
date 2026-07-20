import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from memos_cafe.caja.tests.factories import MesaFactory
from memos_cafe.mesas.models import Mesa
from memos_cafe.roles.models import PermisoRol
from memos_cafe.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def mesero_client():
    grupo, _ = Group.objects.get_or_create(name="mesero")
    usuario = UserFactory()
    usuario.groups.add(grupo)
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


class TestMesaModuloHabilitado:
    """El modulo 'mesas' (PermisoRol) solo gatea las acciones de gestion
    (crear/editar/dar de baja/cambiar estado). list/retrieve queda siempre
    disponible porque Ordenes depende de leer mesas para el selector de
    mesa, sin importar si el modulo 'Mesas' esta habilitado para el rol."""

    def test_mesero_lista_mesas_sin_importar_el_modulo(self, mesero_client):
        MesaFactory()
        PermisoRol.objects.update_or_create(
            modulo="mesas", rol="mesero", defaults={"puede_acceder": False}
        )

        r = mesero_client.get("/api/mesas/")

        assert r.status_code == 200

    def test_mesero_sin_modulo_mesas_no_puede_cambiar_estado(self, mesero_client):
        mesa = MesaFactory(estado=Mesa.Estado.LIBRE)
        PermisoRol.objects.update_or_create(
            modulo="mesas", rol="mesero", defaults={"puede_acceder": False}
        )

        r = mesero_client.patch(f"/api/mesas/{mesa.id}/estado/", {"estado": "reservada"}, format="json")

        assert r.status_code == 403
        mesa.refresh_from_db()
        assert mesa.estado == Mesa.Estado.LIBRE

    def test_mesero_con_modulo_mesas_puede_cambiar_estado(self, mesero_client):
        mesa = MesaFactory(estado=Mesa.Estado.LIBRE)
        PermisoRol.objects.update_or_create(
            modulo="mesas", rol="mesero", defaults={"puede_acceder": True}
        )

        r = mesero_client.patch(f"/api/mesas/{mesa.id}/estado/", {"estado": "reservada"}, format="json")

        assert r.status_code == 200
        mesa.refresh_from_db()
        assert mesa.estado == Mesa.Estado.RESERVADA
