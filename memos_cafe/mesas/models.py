from django.db import models
from auditlog.registry import auditlog

from django.db import models


class Mesa(models.Model):
    class Estado(models.TextChoices):
        LIBRE = "libre", "Libre"
        OCUPADA = "ocupada", "Ocupada"
        RESERVADA = "reservada", "Reservada"

    numero = models.SmallIntegerField(unique=True)
    capacidad = models.SmallIntegerField()
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.LIBRE,
    )
    activo = models.BooleanField(default=True)
    fecha_baja = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "mesa"
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ["numero"]

    def __str__(self):
        return f"Mesa {self.numero} ({self.estado})"

    # --- Lógica de negocio ---

    def ocupar(self):
        """El mesero abre una orden → la mesa pasa a ocupada."""
        if self.estado != self.Estado.LIBRE:
            raise ValueError(f"La mesa {self.numero} no está libre.")
        self.estado = self.Estado.OCUPADA
        self.save(update_fields=["estado"])

    def liberar(self):
        """El cajero cobra la orden → la mesa vuelve a libre."""
        self.estado = self.Estado.LIBRE
        self.save(update_fields=["estado"])

    def dar_de_baja(self):
        """El admin desactiva una mesa (ej: mantenimiento)."""
        from django.utils import timezone
        self.activo = False
        self.estado = self.Estado.LIBRE
        self.fecha_baja = timezone.now()
        self.save(update_fields=["activo", "estado", "fecha_baja"])

auditlog.register(Mesa)