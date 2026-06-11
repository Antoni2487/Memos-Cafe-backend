from decimal import Decimal

from django.db import transaction

from memos_cafe.mesas.models import Mesa
from memos_cafe.ordenes.models import DetalleOrden, Orden
from memos_cafe.productos.models import Producto, Promocion


class OrdenService:
    """Orquesta la creación y gestión de órdenes."""

    @staticmethod
    @transaction.atomic
    def crear_orden(
        usuario,
        tipo_orden: str,
        detalles: list[dict],
        mesa: Mesa | None = None,
    ) -> Orden:
        """
        Crea una orden con sus detalles en una sola transacción.

        Args:
            usuario: Usuario que crea la orden (mesero)
            tipo_orden: 'mesa' o 'llevar'
            detalles: lista de dicts con producto/promocion, cantidad, nota
            mesa: instancia de Mesa (requerida si tipo_orden='mesa')

        Lanza ValueError en condiciones inválidas.
        """
        if tipo_orden == Orden.TipoOrden.MESA and not mesa:
            raise ValueError("Debe asignar una mesa para órdenes de tipo 'mesa'.")

        # Fix 4 — select_for_update: bloquea la fila de la mesa en la DB
        # antes de validar su estado, evitando que dos requests simultáneos
        # asignen la misma mesa a dos órdenes distintas.
        if mesa:
            mesa = Mesa.objects.select_for_update().get(pk=mesa.pk)
            if mesa.estado != Mesa.Estado.LIBRE:
                raise ValueError(f"La mesa {mesa.numero} no está libre.")

        if not detalles:
            raise ValueError("La orden debe tener al menos un ítem.")

        orden = Orden.objects.create(
            usuario=usuario,
            tipo_orden=tipo_orden,
            mesa=mesa,
        )

        if mesa:
            mesa.ocupar()

        # Fix 8 — recalcular_total() fuera del loop: antes se llamaba dentro
        # de DetalleOrden.save() → 1 SELECT + 1 UPDATE por ítem.
        # Ahora se llama una sola vez al final → N INSERTs + 1 recálculo.
        for item in detalles:
            DetalleOrdenService.agregar_detalle(orden=orden, **item)

        orden.recalcular_total()
        orden.refresh_from_db()
        return orden

    @staticmethod
    @transaction.atomic
    def anular_orden(orden: Orden) -> Orden:
        """
        Anula una orden. Solo el admin puede hacer esto.
        La mesa se libera automáticamente dentro de orden.anular()
        via Mesa.liberar() — ambas operaciones quedan en la misma transacción.
        """
        orden.anular()
        return orden


class DetalleOrdenService:
    """Gestiona los ítems individuales dentro de una orden."""

    @staticmethod
    def agregar_detalle(
        orden: Orden,
        cantidad: int,
        nota: str = "",
        producto: Producto | None = None,
        promocion: Promocion | None = None,
    ) -> DetalleOrden:
        """
        Agrega un ítem a una orden abierta.
        El precio_unitario se calcula aquí — NO en DetalleOrden.save().
        recalcular_total() debe llamarse en el service después del loop,
        no dentro de este método, para evitar N queries redundantes.

        Lanza ValueError si la orden no está abierta
        o si no se especifica producto ni promoción.
        """
        if not orden.esta_abierta:
            raise ValueError(
                "No se pueden agregar ítems a una orden cerrada o anulada."
            )

        if not producto and not promocion:
            raise ValueError("Debe especificar al menos un producto o una promoción.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")

        precio_unitario = Decimal("0")
        if producto:
            precio_unitario += producto.precio
        if promocion:
            precio_unitario += promocion.precio

        return DetalleOrden.objects.create(
            orden=orden,
            producto=producto,
            promocion=promocion,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            nota=nota,
        )

    @staticmethod
    def eliminar_detalle(orden: Orden, detalle_id: int) -> bool:
        """
        Elimina un ítem de una orden abierta y recalcula el total.
        Retorna True si el ítem ya había sido enviado a cocina/barra (impreso),
        para que el caller pueda ofrecer imprimir un ticket de anulación.
        """
        if not orden.esta_abierta:
            raise ValueError(
                "No se pueden eliminar ítems de una orden cerrada o anulada."
            )

        try:
            detalle = orden.detalles.get(id=detalle_id)
        except DetalleOrden.DoesNotExist:
            raise ValueError(f"El ítem #{detalle_id} no existe en esta orden.")

        estaba_impreso = detalle.impreso
        detalle.delete()
        orden.recalcular_total()
        return estaba_impreso

    @staticmethod
    def marcar_impreso(orden: Orden, detalle_ids: list[int]) -> None:
        """
        Marca los ítems indicados como impresos (ya enviados a cocina/barra).
        Se llama después de imprimir la comanda exitosamente.
        """
        if not detalle_ids:
            return
        orden.detalles.filter(id__in=detalle_ids).update(impreso=True)