import factory
from decimal import Decimal
from django.utils import timezone
from memos_cafe.productos.models import Categoria, Producto, Promocion


class CategoriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Categoria

    nombre = factory.Sequence(lambda n: f"Categoria {n}")
    activo = True


class ProductoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Producto

    nombre = factory.Sequence(lambda n: f"Producto {n}")
    descripcion = "Descripcion de prueba"
    precio = Decimal("10.00")
    categoria = factory.SubFactory(CategoriaFactory)
    disponible = True
    imagen = None


class PromocionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promocion

    nombre = factory.Sequence(lambda n: f"Promocion {n}")
    descripcion = "Descripcion de prueba"
    precio = Decimal("15.00")
    activo = True
    fecha_inicio = factory.LazyFunction(timezone.localdate)
    fecha_fin = factory.LazyFunction(
        lambda: timezone.localdate() + timezone.timedelta(days=7)
    )
    imagen = None