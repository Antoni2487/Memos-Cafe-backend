from django.conf import settings
from django.db import models

from memos_cafe_backend.ordenes.models import Orden


class Caja(models.Model):
    """Sesión de caja. El cajero abre al inicio del turno y cierra al final."""

    class Estado(models.TextChoices):
        ABIERTA = "abierta", "Abierta"
        CERRADA = "cerrada", "Cerrada"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sesiones_caja",
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ABIERTA,
    )
    monto_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Efectivo con el que se abre el turno.",
    )
    monto_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo contado al cerrar el turno.",
    )
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "caja"
        verbose_name = "Sesión de caja"
        verbose_name_plural = "Sesiones de caja"
        ordering = ["-fecha_apertura"]

    def __str__(self):
        return f"Caja #{self.id} — {self.usuario} ({self.estado})"

    # --- Lógica de negocio ---

    @classmethod
    def get_sesion_abierta(cls):
        """Devuelve la sesión de caja actualmente abierta, o None."""
        return cls.objects.filter(estado=cls.Estado.ABIERTA).first()

    def cerrar(self, monto_final, observaciones=""):
        """El cajero cierra la sesión al final del turno."""
        from django.utils import timezone
        if self.estado != self.Estado.ABIERTA:
            raise ValueError("Esta sesión de caja ya está cerrada.")
        self.estado = self.Estado.CERRADA
        self.monto_final = monto_final
        self.observaciones = observaciones
        self.fecha_cierre = timezone.now()
        self.save(update_fields=["estado", "monto_final", "observaciones", "fecha_cierre"])

    @property
    def total_ventas(self):
        """Suma de todos los pagos exitosos en esta sesión."""
        return self.pagos.filter(
            estado=Pago.Estado.COMPLETADO
        ).aggregate(
            total=models.Sum("monto")
        )["total"] or 0

    @property
    def diferencia(self):
        """Diferencia entre lo esperado y lo contado al cierre."""
        if self.monto_final is None:
            return None
        return self.monto_final - (self.monto_inicial + self.total_ventas)


class MovimientoCaja(models.Model):
    """Registra entradas/salidas de efectivo dentro de una sesión (sin orden asociada)."""

    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"

    caja = models.ForeignKey(
        Caja,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimiento_caja"
        verbose_name = "Movimiento de caja"
        verbose_name_plural = "Movimientos de caja"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} S/.{self.monto} — {self.motivo}"


class Pago(models.Model):
    """Registro del cobro de una orden."""
    class Estado(models.TextChoices):
        COMPLETADO = "completado", "Completado"
        ANULADO = "anulado", "Anulado"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TARJETA = "tarjeta", "Tarjeta"
        YAPE = "yape", "Yape"
        PLIN = "plin", "Plin"

    orden = models.OneToOneField(
        Orden,
        on_delete=models.PROTECT,
        related_name="pago",
    )
    caja = models.ForeignKey(
        Caja,
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    metodo_pago = models.CharField(max_length=10, choices=MetodoPago.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.COMPLETADO,
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pago"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pago Orden #{self.orden_id} — S/.{self.monto}"

    # --- Lógica de negocio ---

    def anular(self):
        """El admin anula un pago por error."""
        if self.estado == self.Estado.ANULADO:
            raise ValueError("Este pago ya está anulado.")
        self.estado = self.Estado.ANULADO
        self.save(update_fields=["estado"])


class Comprobante(models.Model):
    """Boleta o factura emitida al momento del pago."""

    class TipoComprobante(models.TextChoices):
        BOLETA = "boleta", "Boleta"
        FACTURA = "factura", "Factura"

    pago = models.OneToOneField(
        Pago,
        on_delete=models.PROTECT,
        related_name="comprobante",
    )
    tipo = models.CharField(max_length=10, choices=TipoComprobante.choices)
    serie = models.CharField(max_length=10)
    numero = models.PositiveIntegerField()
    # Datos del cliente (necesarios para factura)
    cliente_nombre = models.CharField(max_length=150, blank=True)
    cliente_ruc_dni = models.CharField(max_length=11, blank=True)
    cliente_direccion = models.CharField(max_length=255, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comprobante"
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        # No puede existir dos comprobantes con la misma serie y número
        unique_together = [("serie", "numero")]
        ordering = ["-fecha_emision"]

    def __str__(self):
        return f"{self.tipo.capitalize()} {self.serie}-{self.numero:08d}"