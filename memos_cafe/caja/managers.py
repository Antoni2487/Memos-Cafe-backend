from django.db import models
from django.db.models import Sum, Count, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Value


class CajaManager(models.Manager):
    def get_sesion_abierta(self):
        """Devuelve la sesión de caja actualmente abierta o None."""
        return self.filter(estado="abierta").select_related("usuario").first()

    def get_sesion_abierta_o_error(self):
        """
        Igual que get_sesion_abierta pero lanza ValueError si no hay ninguna.
        Útil en services donde la caja abierta es prerequisito.
        """
        caja = self.get_sesion_abierta()
        if not caja:
            raise ValueError("No hay una sesión de caja abierta.")
        return caja


class PagoManager(models.Manager):
    def completados(self):
        return self.filter(estado="completado")

    def total_por_caja(self, caja):
        """Total de ventas completadas en una sesión de caja."""
        return (
            self.completados()
            .filter(caja=caja)
            .aggregate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                cantidad=Count("id"),
            )
        )

    def desglose_por_metodo(self, caja):
        """Desglose de ventas por método de pago en una sesión."""
        return (
            self.completados()
            .filter(caja=caja)
            .values("metodo_pago")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                cantidad=Count("id"),
            )
            .order_by("-total")
        )