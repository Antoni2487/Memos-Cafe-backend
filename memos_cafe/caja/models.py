# memos_cafe/caja/models.py
from django.conf import settings
from django.db import models

from memos_cafe.caja.managers import CajaManager, PagoManager
from memos_cafe.ordenes.models import Orden


class Caja(models.Model):
    class Estado(models.TextChoices):
        ABIERTA = "abierta", "Abierta"
        CERRADA = "cerrada", "Cerrada"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sesiones_caja",
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTA)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    objects = CajaManager()

    class Meta:
        db_table = "caja"
        verbose_name = "Sesión de caja"
        verbose_name_plural = "Sesiones de caja"
        ordering = ["-fecha_apertura"]

    def __str__(self):
        return f"Caja #{self.id} — {self.usuario} ({self.estado})"

    def cerrar(self, monto_final, observaciones=""):
        from django.utils import timezone
        if self.estado != self.Estado.ABIERTA:
            raise ValueError("Esta sesión de caja ya está cerrada.")
        self.estado = self.Estado.CERRADA
        self.monto_final = monto_final
        self.observaciones = observaciones
        self.fecha_cierre = timezone.now()
        self.save(update_fields=["estado", "monto_final", "observaciones", "fecha_cierre"])

    @property
    def esta_abierta(self):
        return self.estado == self.Estado.ABIERTA


class MovimientoCaja(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"

    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name="movimientos")
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
    class Estado(models.TextChoices):
        COMPLETADO = "completado", "Completado"
        ANULADO = "anulado", "Anulado"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TARJETA = "tarjeta", "Tarjeta"
        YAPE = "yape", "Yape"
        PLIN = "plin", "Plin"

    # ForeignKey en lugar de OneToOneField — permite múltiples pagos por orden
    orden = models.ForeignKey(
        Orden,
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name="pagos")
    metodo_pago = models.CharField(max_length=10, choices=MetodoPago.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recibido = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Solo para efectivo: monto físico entregado por el cliente."
    )
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_operacion = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Número de operación para pagos con tarjeta."
    )
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.COMPLETADO)
    fecha = models.DateTimeField(auto_now_add=True)

    objects = PagoManager()

    class Meta:
        db_table = "pago"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pago Orden #{self.orden_id} — {self.metodo_pago} S/.{self.monto}"

    def anular(self):
        if self.estado == self.Estado.ANULADO:
            raise ValueError("Este pago ya está anulado.")
        self.estado = self.Estado.ANULADO
        self.save(update_fields=["estado"])


class Comprobante(models.Model):
    class TipoComprobante(models.TextChoices):
        BOLETA = "boleta", "Boleta"
        FACTURA = "factura", "Factura"

    # Sigue OneToOne con Pago — un comprobante por pago
    pago = models.OneToOneField(Pago, on_delete=models.PROTECT, related_name="comprobante")
    tipo = models.CharField(max_length=10, choices=TipoComprobante.choices)
    serie = models.CharField(max_length=10)
    numero = models.PositiveIntegerField()
    cliente_nombre = models.CharField(max_length=150, blank=True)
    cliente_ruc_dni = models.CharField(max_length=11, blank=True)
    cliente_direccion = models.CharField(max_length=255, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comprobante"
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        unique_together = [("serie", "numero")]
        ordering = ["-fecha_emision"]

    def __str__(self):
        return f"{self.tipo.capitalize()} {self.serie}-{self.numero:08d}"