import pytest
from django.utils import timezone
from datetime import timedelta
from memos_cafe.productos.tests.factories import (
    CategoriaFactory, ProductoFactory, PromocionFactory
)


pytestmark = pytest.mark.django_db


class TestCategoriaModel:
    def test_str_retorna_nombre(self):
        categoria = CategoriaFactory(nombre="Bebidas")
        assert str(categoria) == "Bebidas"

    def test_activo_por_defecto(self):
        categoria = CategoriaFactory()
        assert categoria.activo is True

    def test_nombre_unico(self):
        from django.db import IntegrityError
        CategoriaFactory(nombre="Cafes")
        with pytest.raises(IntegrityError):
            CategoriaFactory(nombre="Cafes")


class TestProductoModel:
    def test_str_retorna_nombre(self):
        producto = ProductoFactory(nombre="Cappuccino")
        assert str(producto) == "Cappuccino"

    def test_disponible_por_defecto(self):
        producto = ProductoFactory()
        assert producto.disponible is True

    def test_activar(self):
        producto = ProductoFactory(disponible=False)
        producto.activar()
        producto.refresh_from_db()
        assert producto.disponible is True

    def test_desactivar(self):
        producto = ProductoFactory(disponible=True)
        producto.desactivar()
        producto.refresh_from_db()
        assert producto.disponible is False

    def test_precio_mayor_a_cero(self):
        from decimal import Decimal
        producto = ProductoFactory(precio=Decimal("5.50"))
        assert producto.precio > 0

    def test_categoria_protegida_al_eliminar(self):
        from django.db import models
        campo = ProductoFactory._meta.model._meta.get_field("categoria")
        assert campo.remote_field.on_delete == models.PROTECT


class TestPromocionModel:
    def test_str_retorna_nombre(self):
        promo = PromocionFactory(nombre="2x1 Lunes")
        assert str(promo) == "2x1 Lunes"

    def test_esta_vigente_true(self):
        hoy = timezone.localdate()
        promo = PromocionFactory(
            activo=True,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=1),
        )
        assert promo.esta_vigente() is True

    def test_esta_vigente_false_inactivo(self):
        hoy = timezone.localdate()
        promo = PromocionFactory(
            activo=False,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=1),
        )
        assert promo.esta_vigente() is False

    def test_esta_vigente_false_fecha_pasada(self):
        promo = PromocionFactory(
            activo=True,
            fecha_inicio=timezone.localdate() - timedelta(days=10),
            fecha_fin=timezone.localdate() - timedelta(days=1),
        )
        assert promo.esta_vigente() is False

    def test_esta_vigente_false_fecha_futura(self):
        promo = PromocionFactory(
            activo=True,
            fecha_inicio=timezone.localdate() + timedelta(days=2),
            fecha_fin=timezone.localdate() + timedelta(days=5),
        )
        assert promo.esta_vigente() is False