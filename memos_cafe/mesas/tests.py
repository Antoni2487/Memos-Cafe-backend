import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from memos_cafe.caja.tests.factories import MesaFactory
from memos_cafe.mesas.models import Mesa
from memos_cafe.mesas.services import MesaService
from memos_cafe.roles.models import PermisoRol
from memos_cafe.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestMesaServiceCambiarEstado:
    """Cambio de estado de mesa a nivel de servicio (sin pasar por la API).
    Las unicas transiciones manuales permitidas son libre<->reservada; el
    resto (incluyendo cualquier cosa hacia/desde 'ocupada') solo puede
    darse automaticamente vía Mesa.ocupar()/liberar() al crear/cerrar
    una orden, nunca por accion manual."""

    @pytest.fixture
    def mesa_libre(self):
        return MesaFactory(estado=Mesa.Estado.LIBRE)

    @pytest.fixture
    def mesa_reservada(self):
        return MesaFactory(estado=Mesa.Estado.RESERVADA)

    def test_libre_a_reservada(self, mesa_libre):
        MesaService.cambiar_estado(mesa_libre, Mesa.Estado.RESERVADA)
        mesa_libre.refresh_from_db()
        assert mesa_libre.estado == Mesa.Estado.RESERVADA

    def test_reservada_a_libre(self, mesa_reservada):
        MesaService.cambiar_estado(mesa_reservada, Mesa.Estado.LIBRE)
        mesa_reservada.refresh_from_db()
        assert mesa_reservada.estado == Mesa.Estado.LIBRE

    @pytest.mark.parametrize("estado_actual,estado_destino", [
        (Mesa.Estado.OCUPADA, Mesa.Estado.LIBRE),
        (Mesa.Estado.OCUPADA, Mesa.Estado.RESERVADA),
        (Mesa.Estado.LIBRE, Mesa.Estado.OCUPADA),
        (Mesa.Estado.RESERVADA, Mesa.Estado.OCUPADA),
        (Mesa.Estado.LIBRE, Mesa.Estado.LIBRE),
    ])
    def test_transiciones_manuales_invalidas_lanzan_error(self, estado_actual, estado_destino):
        mesa = MesaFactory(estado=estado_actual)
        with pytest.raises(ValueError, match="No se puede cambiar"):
            MesaService.cambiar_estado(mesa, estado_destino)
        mesa.refresh_from_db()
        assert mesa.estado == estado_actual  # no debe mutar nada si falla


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
