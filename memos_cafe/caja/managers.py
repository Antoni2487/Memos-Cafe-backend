from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count, DecimalField, Case, When
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

    def get_sesion_abierta_para_cierre(self):
        """Usa select_for_update para bloquear la fila durante el cierre
        y evitar que dos cierres concurrentes pisen el mismo registro."""
        try:
            return self.select_for_update().get(estado="abierta")
        except ObjectDoesNotExist:
            raise ValueError("No hay una sesión de caja abierta.")


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


class MovimientoCajaManager(models.Manager):
    def neto_por_caja(self, caja):
        """Entradas menos salidas de movimientos manuales de esta caja.
        Debe sumarse al esperado en caja junto con las ventas."""
        resultado = (
            self.filter(caja=caja)
            .aggregate(
                neto=Coalesce(
                    Sum(
                        Case(
                            When(tipo="entrada", then="monto"),
                            When(tipo="salida", then=-models.F("monto")),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0),
                    output_field=DecimalField(),
                )
            )
        )
        return resultado["neto"]
