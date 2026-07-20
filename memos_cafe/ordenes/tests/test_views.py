import pytest
from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from memos_cafe.caja.tests.factories import CajaFactory, MesaFactory
from memos_cafe.mesas.models import Mesa
from memos_cafe.productos.tests.factories import ProductoFactory
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


@pytest.fixture
def cajero_client():
    grupo, _ = Group.objects.get_or_create(name="cajero")
    usuario = UserFactory()
    usuario.groups.add(grupo)
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


class TestOrdenViewSetQuerysetCajero:
    """Cubre OrdenViewSet.get_queryset() para el rol cajero — la rama que
    se toco al mover la consulta de la caja abierta a OrdenService
    (para que la vista no importe memos_cafe.caja.models directamente,
    ver .importlinter)."""

    def test_cajero_ve_ordenes_del_turno_actual(self, cajero_client):
        CajaFactory()  # turno abierto "ahora"
        mesero = UserFactory()
        mesa = MesaFactory(estado=Mesa.Estado.LIBRE)
        producto = ProductoFactory(precio=Decimal("10.00"))
        from memos_cafe.ordenes.services import OrdenService
        OrdenService.crear_orden(
            usuario=mesero, tipo_orden="mesa", mesa=mesa,
            detalles=[{"producto": producto, "cantidad": 1}],
        )

        r = cajero_client.get("/api/ordenes/")

        assert r.status_code == 200
        listado = r.data.get("results", r.data)
        assert len(listado) == 1

    def test_cajero_sin_turno_abierto_no_ve_ordenes(self, cajero_client):
        # A proposito NO se crea CajaFactory(): ningun turno abierto.
        r = cajero_client.get("/api/ordenes/")

        assert r.status_code == 200
        listado = r.data.get("results", r.data)
        assert listado == []


class TestCrearOrdenReflejaMesaOcupadaSinPolling:
    def test_post_ordenes_crear_luego_get_mesas_ya_refleja_ocupada(self, mesero_client):
        """Tras el POST de creacion, un GET /mesas/ inmediato (sin sleep ni
        reintentos) debe devolver la mesa como 'ocupada'. Cubre el flujo
        completo end-to-end que el frontend consume."""
        CajaFactory()
        mesa = MesaFactory(estado=Mesa.Estado.LIBRE)
        producto = ProductoFactory(precio=Decimal("10.00"))

        r_crear = mesero_client.post(
            "/api/ordenes/crear/",
            {
                "tipo_orden": "mesa",
                "mesa": mesa.id,
                "detalles": [{"producto": producto.id, "cantidad": 1}],
            },
            format="json",
        )
        assert r_crear.status_code == 201
        assert r_crear.data["mesa"] == mesa.id

        r_mesas = mesero_client.get("/api/mesas/")
        assert r_mesas.status_code == 200
        listado = r_mesas.data.get("results", r_mesas.data)
        mesa_en_respuesta = next(m for m in listado if m["id"] == mesa.id)
        assert mesa_en_respuesta["estado"] == "ocupada"

    def test_post_ordenes_crear_con_mesa_ya_ocupada_rechaza(self, mesero_client):
        CajaFactory()
        mesa = MesaFactory(estado=Mesa.Estado.OCUPADA)
        producto = ProductoFactory(precio=Decimal("10.00"))

        r_crear = mesero_client.post(
            "/api/ordenes/crear/",
            {
                "tipo_orden": "mesa",
                "mesa": mesa.id,
                "detalles": [{"producto": producto.id, "cantidad": 1}],
            },
            format="json",
        )
        assert r_crear.status_code == 400
