import pytest
from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from memos_cafe.caja.tests.factories import CajaFactory, OrdenFactory
from memos_cafe.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def cajero_client():
    grupo, _ = Group.objects.get_or_create(name="cajero")
    usuario = UserFactory()
    usuario.groups.add(grupo)
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


class TestPagoProcesarSinMontoRecibido:
    """serializer.validated_data['monto_recibido'] tira KeyError cuando el
    campo no viene en el payload (required=False sin default). Pasa en todo
    pago que no sea efectivo, y en efectivo sin monto recibido explicito."""

    def test_pago_con_tarjeta_sin_monto_recibido_no_revienta(self, cajero_client):
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))

        r = cajero_client.post("/api/caja/pagos/procesar/", {
            "orden": orden.id,
            "metodo_pago": "tarjeta",
            "monto": "50.00",
            "numero_operacion": "OP123",
        }, format="json")

        assert r.status_code == 201
        assert r.data["estado"] == "completado"

    def test_pago_efectivo_sin_monto_recibido_no_revienta(self, cajero_client):
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("30.00"))

        r = cajero_client.post("/api/caja/pagos/procesar/", {
            "orden": orden.id,
            "metodo_pago": "efectivo",
            "monto": "30.00",
        }, format="json")

        assert r.status_code == 201

    def test_pago_efectivo_con_monto_recibido_calcula_vuelto(self, cajero_client):
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("30.00"))

        r = cajero_client.post("/api/caja/pagos/procesar/", {
            "orden": orden.id,
            "metodo_pago": "efectivo",
            "monto": "30.00",
            "monto_recibido": "50.00",
        }, format="json")

        assert r.status_code == 201
        assert Decimal(r.data["vuelto"]) == Decimal("20.00")
