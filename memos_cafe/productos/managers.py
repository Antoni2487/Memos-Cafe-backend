from django.db import models


class ProductoManager(models.Manager):
    def disponibles(self):
        """Solo productos activos y disponibles en carta."""
        return self.filter(disponible=True).select_related("categoria")

    def por_categoria(self, categoria_id):
        """Productos disponibles filtrados por categoría."""
        return self.disponibles().filter(categoria_id=categoria_id)

    def con_categoria(self):
        """Todos los productos con su categoría — evita N+1."""
        return self.select_related("categoria").all()


class PromocionManager(models.Manager):
    def vigentes(self):
        """Promociones activas dentro del rango de fechas actual."""
        from django.utils import timezone
        hoy = timezone.localdate()
        return self.filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )

    def todas_activas(self):
        """Todas las promociones marcadas como activas (sin filtro de fecha)."""
        return self.filter(activo=True)