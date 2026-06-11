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
        cliente_nombre: str = "",
        cliente_telefono: str = "",
        direccion_entrega: str = "",
        plataforma_delivery: str = "",
        plataforma_otra: str = "",
    ) -> Orden:
        if tipo_orden == Orden.TipoOrden.MESA and not mesa:
            raise ValueError("Debe asignar una mesa para órdenes de tipo 'mesa'.")

        if tipo_orden == Orden.TipoOrden.DELIVERY and not plataforma_delivery:
            raise ValueError("Debe especificar la plataforma para órdenes delivery.")

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
            cliente_nombre=cliente_nombre,
            cliente_telefono=cliente_telefono,
            direccion_entrega=direccion_entrega,
            plataforma_delivery=plataforma_delivery if tipo_orden == Orden.TipoOrden.DELIVERY else "",
            plataforma_otra=plataforma_otra if tipo_orden == Orden.TipoOrden.DELIVERY else "",
        )

        if mesa:
            mesa.ocupar()

        for item in detalles:
            DetalleOrdenService._crear_detalle(orden=orden, **item)

        orden.recalcular_total()
        orden.refresh_from_db()
        return orden

    @staticmethod
    @transaction.atomic
    def anular_orden(orden: Orden) -> Orden:
        orden.anular()
        return orden


class DetalleOrdenService:
    """Gestiona los ítems individuales dentro de una orden."""

    @staticmethod
    def _crear_detalle(
        orden: Orden,
        cantidad: int,
        nota: str = "",
        producto: Producto | None = None,
        promocion: Promocion | None = None,
    ) -> DetalleOrden:
        """
        Uso interno — crear_orden() lo llama dentro del loop.
        No llama recalcular_total(); el caller lo hace una sola vez al final.
        """
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
    @transaction.atomic
    def agregar_detalle(
        orden: Orden,
        cantidad: int,
        nota: str = "",
        producto: Producto | None = None,
        promocion: Promocion | None = None,
    ) -> DetalleOrden:
        """
        API pública — agrega un ítem a una orden ya existente.
        Recalcula el total de la orden al finalizar.
        """
        if not orden.esta_abierta:
            raise ValueError("No se pueden agregar ítems a una orden cerrada o anulada.")

        detalle = DetalleOrdenService._crear_detalle(
            orden=orden,
            cantidad=cantidad,
            nota=nota,
            producto=producto,
            promocion=promocion,
        )
        orden.recalcular_total()
        return detalle

    @staticmethod
    @transaction.atomic
    def eliminar_detalle(orden: Orden, detalle_id: int) -> bool:
        """
        Elimina un ítem de una orden abierta y recalcula el total.
        Retorna True si el ítem ya había sido enviado a cocina/barra (impreso),
        para que el caller pueda ofrecer imprimir un ticket de anulación.
        """
        if not orden.esta_abierta:
            raise ValueError("No se pueden eliminar ítems de una orden cerrada o anulada.")

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
