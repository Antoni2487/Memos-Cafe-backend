from django.db import models
from django.db.models import Prefetch


class OrdenManager(models.Manager):
    def abiertas(self):
        """Órdenes abiertas con detalles prefetcheados — evita N+1."""
        from memos_cafe.ordenes.models import DetalleOrden
        return (
            self.filter(estado="abierta")
            .select_related("mesa", "usuario")
            .prefetch_related(
                Prefetch(
                    "detalles",
                    queryset=DetalleOrden.objects.select_related(
                        "producto", "producto__categoria", "promocion"
                    ),
                )
            )
        )

    def abiertas_por_usuario(self, usuario):
        """Órdenes abiertas de un mesero específico."""
        return self.abiertas().filter(usuario=usuario)

    def con_detalles(self):
        """Cualquier orden con sus detalles prefetcheados."""
        from memos_cafe.ordenes.models import DetalleOrden
        return self.select_related("mesa", "usuario").prefetch_related(
            Prefetch(
                "detalles",
                queryset=DetalleOrden.objects.select_related(
                    "producto", "producto__categoria", "promocion"
                ),
            )
        )