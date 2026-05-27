from django.db import models
from django.utils import timezone

from memos_cafe.productos.managers import ProductoManager, PromocionManager


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "categoria"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    disponible = models.BooleanField(default=True)
    imagen_url = models.CharField(max_length=255, blank=True)

    objects = ProductoManager()

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["categoria", "nombre"]

    def __str__(self):
        return self.nombre

    def activar(self):
        self.disponible = True
        self.save(update_fields=["disponible"])

    def desactivar(self):
        self.disponible = False
        self.save(update_fields=["disponible"])


class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen_url = models.CharField(max_length=255, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    objects = PromocionManager()

    class Meta:
        db_table = "promocion"
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ["fecha_fin"]

    def __str__(self):
        return self.nombre

    def esta_vigente(self):
        hoy = timezone.localdate()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin