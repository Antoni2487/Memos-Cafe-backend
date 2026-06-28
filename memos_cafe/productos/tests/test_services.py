import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from memos_cafe.productos.services import (
    CategoriaService, ProductoService, PromocionService
)
from memos_cafe.productos.tests.factories import (
    CategoriaFactory, ProductoFactory, PromocionFactory
)

pytestmark = pytest.mark.django_db


class TestCategoriaService:
    def test_crear_categoria(self):
        cat = CategoriaService.crear("Postres")
        assert cat.nombre == "Postres"
        assert cat.activo is True

    def test_crear_categoria_duplicada_lanza_error(self):
        CategoriaService.crear("Bebidas")
        with pytest.raises(ValueError, match="Ya existe"):
            CategoriaService.crear("Bebidas")

    def test_crear_categoria_duplicada_case_insensitive(self):
        CategoriaService.crear("Bebidas")
        with pytest.raises(ValueError):
            CategoriaService.crear("bebidas")

    def test_editar_categoria(self):
        cat = CategoriaFactory(nombre="Viejo")
        result = CategoriaService.editar(cat, "Nuevo")
        assert result.nombre == "Nuevo"

    def test_editar_categoria_nombre_vacio_lanza_error(self):
        cat = CategoriaFactory()
        with pytest.raises(ValueError, match="vacío"):
            CategoriaService.editar(cat, "   ")

    def test_editar_categoria_nombre_duplicado_lanza_error(self):
        CategoriaFactory(nombre="Existente")
        cat = CategoriaFactory(nombre="Otra")
        with pytest.raises(ValueError, match="Ya existe"):
            CategoriaService.editar(cat, "Existente")

    def test_activar_categoria(self):
        cat = CategoriaFactory(activo=False)
        CategoriaService.activar(cat)
        cat.refresh_from_db()
        assert cat.activo is True

    def test_desactivar_categoria(self):
        cat = CategoriaFactory(activo=True)
        CategoriaService.desactivar(cat)
        cat.refresh_from_db()
        assert cat.activo is False

    def test_desactivar_categoria_con_productos_lanza_error(self):
        cat = CategoriaFactory()
        ProductoFactory(categoria=cat, disponible=True)
        with pytest.raises(ValueError, match="productos disponibles"):
            CategoriaService.desactivar(cat)


class TestProductoService:
    def test_crear_producto(self):
        cat = CategoriaFactory()
        p = ProductoService.crear("Latte", Decimal("12.00"), cat)
        assert p.nombre == "Latte"
        assert p.precio == Decimal("12.00")
        assert p.disponible is True

    def test_crear_producto_precio_cero_lanza_error(self):
        cat = CategoriaFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            ProductoService.crear("X", Decimal("0"), cat)

    def test_crear_producto_precio_negativo_lanza_error(self):
        cat = CategoriaFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            ProductoService.crear("X", Decimal("-5"), cat)

    def test_editar_producto_precio(self):
        p = ProductoFactory(precio=Decimal("10.00"))
        ProductoService.editar(p, precio=Decimal("20.00"))
        p.refresh_from_db()
        assert p.precio == Decimal("20.00")

    def test_editar_producto_disponible_false(self):
        p = ProductoFactory(disponible=True)
        ProductoService.editar(p, disponible=False)
        p.refresh_from_db()
        assert p.disponible is False

    def test_editar_producto_precio_invalido_lanza_error(self):
        p = ProductoFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            ProductoService.editar(p, precio=Decimal("-1"))

    def test_actualizar_precio(self):
        p = ProductoFactory(precio=Decimal("10.00"))
        ProductoService.actualizar_precio(p, Decimal("25.00"))
        p.refresh_from_db()
        assert p.precio == Decimal("25.00")

    def test_actualizar_precio_cero_lanza_error(self):
        p = ProductoFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            ProductoService.actualizar_precio(p, Decimal("0"))


class TestPromocionService:
    def test_crear_promocion(self):
        hoy = timezone.localdate()
        promo = PromocionService.crear(
            nombre="Happy Hour",
            precio=Decimal("10.00"),
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=5),
        )
        assert promo.nombre == "Happy Hour"
        assert promo.activo is True

    def test_crear_promocion_precio_invalido_lanza_error(self):
        hoy = timezone.localdate()
        with pytest.raises(ValueError, match="mayor a 0"):
            PromocionService.crear(
                nombre="X", precio=Decimal("0"),
                fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=1),
            )

    def test_crear_promocion_fecha_inicio_pasado_lanza_error(self):
        hoy = timezone.localdate()
        with pytest.raises(ValueError, match="pasado"):
            PromocionService.crear(
                nombre="X", precio=Decimal("5.00"),
                fecha_inicio=hoy - timedelta(days=1),
                fecha_fin=hoy + timedelta(days=1),
            )

    def test_crear_promocion_fecha_fin_antes_inicio_lanza_error(self):
        hoy = timezone.localdate()
        with pytest.raises(ValueError, match="anterior"):
            PromocionService.crear(
                nombre="X", precio=Decimal("5.00"),
                fecha_inicio=hoy + timedelta(days=3),
                fecha_fin=hoy + timedelta(days=1),
            )

    def test_activar_promocion(self):
        promo = PromocionFactory(activo=False)
        PromocionService.activar(promo)
        promo.refresh_from_db()
        assert promo.activo is True

    def test_desactivar_promocion(self):
        promo = PromocionFactory(activo=True)
        PromocionService.desactivar(promo)
        promo.refresh_from_db()
        assert promo.activo is False

    def test_editar_promocion_precio_invalido_lanza_error(self):
        promo = PromocionFactory()
        with pytest.raises(ValueError, match="mayor a 0"):
            PromocionService.editar(promo, precio=Decimal("-1"))

    def test_editar_promocion_fechas_invalidas_lanza_error(self):
        hoy = timezone.localdate()
        promo = PromocionFactory(
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=5),
        )
        with pytest.raises(ValueError, match="anterior"):
            PromocionService.editar(
                promo,
                fecha_fin=hoy - timedelta(days=1),
            )