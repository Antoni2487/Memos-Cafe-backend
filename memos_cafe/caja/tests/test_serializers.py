import pytest
from decimal import Decimal

from memos_cafe.caja.api.serializers import ComprobanteWriteSerializer
from memos_cafe.caja.models import Pago
from memos_cafe.caja.tests.factories import CajaFactory, OrdenFactory

pytestmark = pytest.mark.django_db


def _crear_pago_completado():
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
    def test_ruc_valido_pasa(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", "12345678901"))
        assert serializer.is_valid(), serializer.errors

    def test_ruc_con_letras_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", "1234567890A"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_ruc_con_menos_digitos_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", "1234567890"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_ruc_con_mas_digitos_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", "123456789012"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_ruc_vacio_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", ""))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_dni_de_8_digitos_en_una_factura_falla(self):
        """Tipo de comprobante equivocado: una factura exige RUC (11), no DNI (8)."""
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "factura", "12345678"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_sin_nombre_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(
            data=_payload(pago, "factura", "12345678901", cliente_nombre="")
        )
        assert not serializer.is_valid()
        assert "cliente_nombre" in serializer.errors


class TestComprobanteWriteSerializerBoleta:
    def test_dni_valido_pasa(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", "12345678"))
        assert serializer.is_valid(), serializer.errors

    def test_sin_dni_pasa(self):
        """En boleta el DNI es opcional (consumidor final anónimo)."""
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", ""))
        assert serializer.is_valid(), serializer.errors

    def test_dni_con_letras_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", "1234567A"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_dni_con_menos_digitos_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", "1234567"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_dni_con_mas_digitos_falla(self):
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", "123456789"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors

    def test_ruc_de_11_digitos_en_una_boleta_falla(self):
        """Tipo de comprobante equivocado: una boleta exige DNI (8), no RUC (11)."""
        pago = _crear_pago_completado()
        serializer = ComprobanteWriteSerializer(data=_payload(pago, "boleta", "12345678901"))
        assert not serializer.is_valid()
        assert "cliente_ruc_dni" in serializer.errors
