from django.conf import settings
from django.db import models


class TipoInsumo(models.Model):
    """Catálogo de insumos que usa la cafetería (azúcar, café, leche, etc.)."""

    class Unidad(models.TextChoices):
        KILOGRAMO = "kg", "Kilogramo"
        GRAMO = "g", "Gramo"
        LITRO = "l", "Litro"
        MILILITRO = "ml", "Mililitro"
        UNIDAD = "und", "Unidad"

    nombre = models.CharField(max_length=100, unique=True)
    unidad = models.CharField(max_length=5, choices=Unidad.choices)
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Nivel mínimo antes de generar alerta de reposición.",
    )
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipo_insumo"
        verbose_name = "Tipo de insumo"
        verbose_name_plural = "Tipos de insumo"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.unidad})"

    # --- Lógica de negocio ---

    @property
    def stock_bajo(self):
        """True si el stock actual está por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo


class RegistroInsumo(models.Model):
    """Historial de compras/entradas de insumos."""

    insumo = models.ForeignKey(
        TipoInsumo,
        on_delete=models.PROTECT,
        related_name="registros",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registros_insumo",
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.CharField(max_length=150, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "registro_insumo"
        verbose_name = "Registro de insumo"
        verbose_name_plural = "Registros de insumos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.insumo} x{self.cantidad} — {self.fecha:%d/%m/%Y}"

    # --- Lógica de negocio ---

    def save(self, *args, **kwargs):
        """Calcula el costo total y actualiza el stock del insumo al guardar."""
        self.costo_total = self.costo_unitario * self.cantidad
        super().save(*args, **kwargs)
        # Actualiza stock en TipoInsumo
        self.insumo.stock_actual = (
            self.insumo.registros.aggregate(
                total=models.Sum("cantidad")
            )["total"] or 0
        )
        self.insumo.save(update_fields=["stock_actual"])