import factory
from decimal import Decimal
from memos_cafe.caja.models import Caja, MovimientoCaja, Pago
from memos_cafe.users.tests.factories import UserFactory
from memos_cafe.mesas.models import Mesa
from memos_cafe.ordenes.models import Orden


class CajaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Caja

    usuario = factory.SubFactory(UserFactory)
    estado = Caja.Estado.ABIERTA
    monto_inicial = Decimal("100.00")
    monto_final = None
    observaciones = ""


class MesaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mesa

    numero = factory.Sequence(lambda n: n + 1)
    capacidad = 4
    estado = Mesa.Estado.LIBRE


class OrdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Orden

    mesa = factory.SubFactory(MesaFactory)
    usuario = factory.SubFactory(UserFactory)
    estado = Orden.Estado.ABIERTA
    tipo_orden = Orden.TipoOrden.MESA
    total = Decimal("50.00")