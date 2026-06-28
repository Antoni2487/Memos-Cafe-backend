# memos_cafe/caja/managers.py — sin cambios estructurales, igual que antes
from django.db import models
from django.db.models import Sum, Count, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Value


class CajaManager(models.Manager):
    def get_sesion_abierta(self):
        return self.filter(estado="abierta").select_related("usuario").first()

    def get_sesion_abierta_o_error(self):
        caja = self.get_sesion_abierta()
        if not caja:
            raise ValueError("No hay una sesión de caja abierta.")
        return caja


class PagoManager(models.Manager):
    def completados(self):
        return self.filter(estado="completado")

    def total_por_caja(self, caja):
        return (
            self.completados()
            .filter(caja=caja)
            .aggregate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                cantidad=Count("id"),
            )
        )

    def desglose_por_metodo(self, caja):
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