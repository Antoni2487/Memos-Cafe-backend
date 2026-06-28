import pytest
from decimal import Decimal
from memos_cafe.caja.services import CajaService, PagoService, ComprobanteService
from memos_cafe.caja.models import Caja, MovimientoCaja, Pago, Comprobante
from memos_cafe.caja.tests.factories import CajaFactory, OrdenFactory
from memos_cafe.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCajaService:
    def test_abrir_sesion(self):
        user = UserFactory()
        caja = CajaService.abrir_sesion(user, Decimal("200.00"))
        assert caja.estado == Caja.Estado.ABIERTA
        assert caja.monto_inicial == Decimal("200.00")
        assert caja.usuario == user

    def test_abrir_sesion_ya_existe_lanza_error(self):
        user = UserFactory()
        CajaFactory()  # caja ya abierta
        with pytest.raises(ValueError, match="Ya existe"):
            CajaService.abrir_sesion(user, Decimal("100.00"))

    def test_cerrar_sesion(self):
        CajaFactory()
        caja = CajaService.cerrar_sesion(Decimal("350.00"), "Cierre normal")
        assert caja.estado == Caja.Estado.CERRADA
        assert caja.monto_final == Decimal("350.00")
        assert caja.fecha_cierre is not None

    def test_cerrar_sesion_sin_caja_abierta_lanza_error(self):
        with pytest.raises(ValueError, match="No hay"):
            CajaService.cerrar_sesion(Decimal("100.00"))

    def test_cerrar_sesion_con_observaciones(self):
        CajaFactory()
        caja = CajaService.cerrar_sesion(Decimal("100.00"), "Faltaron S/5")
        assert caja.observaciones == "Faltaron S/5"

    def test_monto_inicial_cero_permitido(self):
        user = UserFactory()
        caja = CajaService.abrir_sesion(user, Decimal("0.00"))
        assert caja.monto_inicial == Decimal("0.00")

    def test_registrar_movimiento_entrada(self):
        CajaFactory()
        mov = CajaService.registrar_movimiento(
            tipo=MovimientoCaja.Tipo.ENTRADA,
            monto=Decimal("50.00"),
            motivo="Fondo adicional",
        )
        assert mov.tipo == MovimientoCaja.Tipo.ENTRADA
        assert mov.monto == Decimal("50.00")

    def test_registrar_movimiento_salida(self):
        CajaFactory()
        mov = CajaService.registrar_movimiento(
            tipo=MovimientoCaja.Tipo.SALIDA,
            monto=Decimal("20.00"),
            motivo="Compra de insumos",
        )
        assert mov.tipo == MovimientoCaja.Tipo.SALIDA

    def test_registrar_movimiento_monto_cero_lanza_error(self):
        CajaFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            CajaService.registrar_movimiento(
                tipo=MovimientoCaja.Tipo.ENTRADA,
                monto=Decimal("0"),
                motivo="test",
            )

    def test_registrar_movimiento_sin_caja_abierta_lanza_error(self):
        with pytest.raises(ValueError, match="No hay"):
            CajaService.registrar_movimiento(
                tipo=MovimientoCaja.Tipo.ENTRADA,
                monto=Decimal("50.00"),
                motivo="test",
            )


class TestCajaModel:
    def test_esta_abierta_property(self):
        caja = CajaFactory()
        assert caja.esta_abierta is True

    def test_cerrar_modelo(self):
        caja = CajaFactory()
        caja.cerrar(Decimal("200.00"), "ok")
        assert caja.estado == Caja.Estado.CERRADA

    def test_cerrar_caja_ya_cerrada_lanza_error(self):
        caja = CajaFactory(estado=Caja.Estado.CERRADA)
        with pytest.raises(ValueError, match="ya está cerrada"):
            caja.cerrar(Decimal("100.00"))


class TestPagoService:
    def test_procesar_pago_exitoso(self):
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("60.00"),
        )
        assert pago.monto == Decimal("60.00")
        assert pago.vuelto == Decimal("10.00")
        assert pago.estado == Pago.Estado.COMPLETADO

    def test_procesar_pago_cierra_orden(self):
        from memos_cafe.ordenes.models import Orden
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("30.00"))
        PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.YAPE,
            monto=Decimal("30.00"),
        )
        orden.refresh_from_db()
        assert orden.estado == Orden.Estado.CERRADA

    def test_procesar_pago_monto_insuficiente_lanza_error(self):
        CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        with pytest.raises(ValueError, match="insuficiente"):
            PagoService.procesar_pago(
                orden=orden,
                metodo_pago=Pago.MetodoPago.EFECTIVO,
                monto=Decimal("30.00"),
            )

    def test_procesar_pago_orden_no_abierta_lanza_error(self):
        CajaFactory()
        orden = OrdenFactory(estado="cerrada", total=Decimal("50.00"))
        with pytest.raises(ValueError, match="abiertas"):
            PagoService.procesar_pago(
                orden=orden,
                metodo_pago=Pago.MetodoPago.EFECTIVO,
                monto=Decimal("50.00"),
            )

    def test_procesar_pago_orden_ya_pagada_lanza_error(self):
        from memos_cafe.caja.models import Pago as PagoModel
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        PagoModel.objects.create(
            orden=orden, caja=caja,
            metodo_pago="efectivo", monto=Decimal("50.00"), vuelto=Decimal("0"),
        )
        with pytest.raises(ValueError, match="ya tiene un pago"):
            PagoService.procesar_pago(
                orden=orden,
                metodo_pago=Pago.MetodoPago.EFECTIVO,
                monto=Decimal("50.00"),
            )

    def test_anular_pago(self):
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("50.00"),
        )
        PagoService.anular_pago(pago)
        pago.refresh_from_db()
        assert pago.estado == Pago.Estado.ANULADO

    def test_anular_pago_genera_movimiento_salida(self):
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("50.00"),
        )
        PagoService.anular_pago(pago)
        mov = MovimientoCaja.objects.filter(
            caja=caja, tipo=MovimientoCaja.Tipo.SALIDA
        ).last()
        assert mov is not None
        assert mov.monto == Decimal("50.00")


class TestComprobanteService:
    def test_emitir_boleta(self):
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("50.00"),
        )
        comp = ComprobanteService.emitir(
            pago=pago, tipo="boleta",
            serie="B001", numero=1,
        )
        assert comp.tipo == "boleta"
        assert str(comp) == "Boleta B001-00000001"

    def test_emitir_factura_sin_ruc_lanza_error(self):
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("50.00"),
        )
        with pytest.raises(ValueError, match="RUC"):
            ComprobanteService.emitir(
                pago=pago, tipo="factura",
                serie="F001", numero=1,
                cliente_nombre="Empresa SAC",
            )

    def test_emitir_comprobante_duplicado_lanza_error(self):
        caja = CajaFactory()
        orden = OrdenFactory(estado="abierta", total=Decimal("50.00"))
        pago = PagoService.procesar_pago(
            orden=orden,
            metodo_pago=Pago.MetodoPago.EFECTIVO,
            monto=Decimal("50.00"),
        )
        ComprobanteService.emitir(pago=pago, tipo="boleta", serie="B001", numero=1)
        with pytest.raises(ValueError, match="ya tiene un comprobante"):
            ComprobanteService.emitir(pago=pago, tipo="boleta", serie="B001", numero=2)