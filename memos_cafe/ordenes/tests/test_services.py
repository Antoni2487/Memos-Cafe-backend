import pytest
from decimal import Decimal

from memos_cafe.caja.tests.factories import CajaFactory, MesaFactory
from memos_cafe.mesas.models import Mesa
from memos_cafe.ordenes.services import OrdenService
from memos_cafe.productos.tests.factories import ProductoFactory
from memos_cafe.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestOrdenServiceCrearOrdenOcupaMesa:
    def test_crear_orden_mesa_ocupa_la_mesa_en_la_misma_transaccion(self):
        """OrdenService.crear_orden debe dejar la mesa 'ocupada' apenas retorna,
        sin depender de ningun paso posterior (async, señal, polling, etc.)."""
        CajaFactory()
        usuario = UserFactory()
        mesa = MesaFactory(estado=Mesa.Estado.LIBRE)
        producto = ProductoFactory(precio=Decimal("10.00"))

        orden = OrdenService.crear_orden(
            usuario=usuario,
            tipo_orden="mesa",
            mesa=mesa,
            detalles=[{"producto": producto, "cantidad": 2}],
        )

        assert orden.mesa_id == mesa.id
        mesa.refresh_from_db()
        assert mesa.estado == Mesa.Estado.OCUPADA

    def test_crear_orden_llevar_no_toca_ninguna_mesa(self):
        """Ordenes para llevar no deben ocupar mesas: confirma que el efecto
        es especifico a tipo_orden='mesa', no un side-effect global."""
        CajaFactory()
        usuario = UserFactory()
        producto = ProductoFactory(precio=Decimal("10.00"))

        orden = OrdenService.crear_orden(
            usuario=usuario,
            tipo_orden="llevar",
            detalles=[{"producto": producto, "cantidad": 1}],
        )

        assert orden.mesa_id is None

    def test_crear_orden_mesa_no_libre_lanza_error_y_no_crea_orden(self):
        from memos_cafe.ordenes.models import Orden

        CajaFactory()
        usuario = UserFactory()
        mesa = MesaFactory(estado=Mesa.Estado.OCUPADA)
        producto = ProductoFactory(precio=Decimal("10.00"))

        with pytest.raises(ValueError, match="no esta libre"):
            OrdenService.crear_orden(
                usuario=usuario,
                tipo_orden="mesa",
                mesa=mesa,
                detalles=[{"producto": producto, "cantidad": 1}],
            )

        assert not Orden.objects.filter(mesa=mesa).exists()
