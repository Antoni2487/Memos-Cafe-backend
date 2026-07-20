import pytest
from decimal import Decimal

from memos_cafe.caja.api.serializers import ComprobanteWriteSerializer
from memos_cafe.caja.models import Pago
from memos_cafe.caja.tests.factories import CajaFactory, OrdenFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def pago_completado():
    caja = CajaFactory()
    orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
    return Pago.objects.create(
        orden=orden, caja=caja, metodo_pago="efectivo",
        monto=Decimal("50.00"), vuelto=Decimal("0"), estado="completado",
    )


def _payload(pago, tipo, cliente_ruc_dni="", cliente_nombre="Cliente de Prueba"):
    return {
        "pago": pago.id,
        "tipo": tipo,
        "serie": "B001",
        "numero": 1,
        "cliente_nombre": cliente_nombre,
        "cliente_ruc_dni": cliente_ruc_dni,
    }


class TestComprobanteWriteSerializerFactura:
    def test_ruc_valido_pasa(self, pago_completado):
        serializer = ComprobanteWriteSerializer(data=_payload(pago_completado, "factura", "12345678901"))
        assert serializer.is_valid(), serializer.errors

    @pytest.mark.parametrize("ruc_invalido", [
        pytest.param("1234567890A", id="con-letras"),
        pytest.param("1234567890", id="10-digitos-de-menos"),
        pytest.param("123456789012", id="12-digitos-de-mas"),
        pytest.param("", id="vacio"),
        pytest.param("12345678", id="dni-de-8-digitos-tipo-equivocado"),
    ])
    def test_ruc_invalido_falla(self, pago_completado, ruc_invalido):
        serializer = ComprobanteWriteSerializer(data=_payload(pago_completado, "factura", ruc_invalido))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_sin_nombre_falla(self, pago_completado):
        serializer = ComprobanteWriteSerializer(
            data=_payload(pago_completado, "factura", "12345678901", cliente_nombre="")
        )
        assert not serializer.is_valid()
        assert "cliente_nombre" in serializer.errors


class TestComprobanteWriteSerializerBoleta:
    def test_dni_valido_pasa(self, pago_completado):
        serializer = ComprobanteWriteSerializer(data=_payload(pago_completado, "boleta", "12345678"))
        assert serializer.is_valid(), serializer.errors

    def test_sin_dni_pasa(self, pago_completado):
        """En boleta el DNI es opcional (consumidor final anónimo)."""
        serializer = ComprobanteWriteSerializer(data=_payload(pago_completado, "boleta", ""))
        assert serializer.is_valid(), serializer.errors

    @pytest.mark.parametrize("dni_invalido", [
        pytest.param("1234567A", id="con-letras"),
        pytest.param("1234567", id="7-digitos-de-menos"),
        pytest.param("123456789", id="9-digitos-de-mas"),
        pytest.param("12345678901", id="ruc-de-11-digitos-tipo-equivocado"),
    ])
    def test_dni_invalido_falla(self, pago_completado, dni_invalido):
        serializer = ComprobanteWriteSerializer(data=_payload(pago_completado, "boleta", dni_invalido))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors
