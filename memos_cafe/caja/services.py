from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum

from memos_cafe.caja.models import Caja, Comprobante, MovimientoCaja, Pago
from memos_cafe.ordenes.models import Orden


class CajaService:

    @staticmethod
    @transaction.atomic
    def abrir_sesion(usuario, monto_inicial: Decimal) -> Caja:
        if Caja.objects.get_sesion_abierta():
            raise ValueError("Ya existe una sesion de caja abierta. Cierrela antes de abrir una nueva.")
        try:
            return Caja.objects.create(usuario=usuario, monto_inicial=monto_inicial)
        except IntegrityError:
            raise ValueError("Ya existe una sesion de caja abierta. Cierrela antes de abrir una nueva.")

    @staticmethod
    @transaction.atomic
    def cerrar_sesion(monto_final: Decimal, observaciones: str = "") -> Caja:
        caja = Caja.objects.get_sesion_abierta_para_cierre()
        caja.cerrar(monto_final=monto_final, observaciones=observaciones)
        return caja

    @staticmethod
    def registrar_movimiento(tipo: str, monto: Decimal, motivo: str) -> MovimientoCaja:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0.")
        caja = Caja.objects.get_sesion_abierta_o_error()
        return MovimientoCaja.objects.create(caja=caja, tipo=tipo, monto=monto, motivo=motivo)


class PagoService:

    @staticmethod
    @transaction.atomic
    def procesar_pago(
        orden: Orden,
        metodo_pago: str,
        monto: Decimal,
        monto_recibido: Decimal = None,
        numero_operacion: str = "",
    ) -> Pago:

        # Lock de fila: evita que dos requests concurrentes sobre la misma
        # orden lean el mismo estado "pre-cobro" y generen doble pago.
        orden = Orden.objects.select_for_update().get(pk=orden.pk)

        if orden.estado != Orden.Estado.ABIERTA:
            raise ValueError("Solo se pueden cobrar ordenes abiertas.")

        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0.")

        pagado_previo = (
            Pago.objects
            .filter(orden=orden, estado=Pago.Estado.COMPLETADO)
            .aggregate(total=Sum("monto"))["total"] or Decimal("0")
        )
        pendiente = orden.total - pagado_previo

        if pendiente <= 0:
            raise ValueError("Esta orden ya esta completamente pagada.")

        if monto > pendiente:
            raise ValueError(
                f"El monto ingresado (S/.{monto}) supera el pendiente (S/.{pendiente:.2f})."
            )

        vuelto = Decimal("0")
        es_ultimo_pago = monto == pendiente

        if metodo_pago == Pago.MetodoPago.EFECTIVO and es_ultimo_pago:
            recibido = monto_recibido if monto_recibido is not None else monto
            if recibido < monto:
                raise ValueError(
                    f"Monto recibido insuficiente. Se deben cubrir S/.{monto:.2f}."
                )
            vuelto = recibido - monto
        elif metodo_pago == Pago.MetodoPago.EFECTIVO and monto_recibido is not None:
            if monto_recibido < monto:
                raise ValueError(
                    f"Monto recibido insuficiente. Se deben cubrir S/.{monto:.2f}."
                )

        caja = Caja.objects.get_sesion_abierta_o_error()

        pago = Pago.objects.create(
            orden=orden,
            caja=caja,
            metodo_pago=metodo_pago,
            monto=monto,
            monto_recibido=monto_recibido if metodo_pago == Pago.MetodoPago.EFECTIVO else None,
            vuelto=vuelto,
            numero_operacion=numero_operacion if metodo_pago == Pago.MetodoPago.TARJETA else "",
        )

        total_pagado = pagado_previo + monto
        if total_pagado >= orden.total:
            orden.cerrar()

        return pago

    @staticmethod
    @transaction.atomic
    def anular_pago(pago: Pago) -> Pago:
        if pago.estado == Pago.Estado.ANULADO:
            raise ValueError("Este pago ya esta anulado.")

        orden = Orden.objects.select_for_update().get(pk=pago.orden_id)
        if orden.estado == Orden.Estado.ANULADA:
            raise ValueError("La orden asociada a este pago ya esta anulada.")

        pago.anular()

        MovimientoCaja.objects.create(
            caja=pago.caja,
            tipo=MovimientoCaja.Tipo.SALIDA,
            monto=pago.monto,
            motivo=f"Devolucion por anulacion de pago #{pago.id} - Orden #{orden.id}",
        )

        # Si la orden estaba cerrada por este pago y, tras anularlo, ya no
        # queda cobertura completa del total, se reabre para que vuelva a
        # aparecer en "por cobrar" y el negocio no pierda esa venta.
        if orden.estado == Orden.Estado.CERRADA:
            pagado_restante = (
                Pago.objects
                .filter(orden=orden, estado=Pago.Estado.COMPLETADO)
                .aggregate(total=Sum("monto"))["total"] or Decimal("0")
            )
            if pagado_restante < orden.total:
                orden.reabrir()

        return pago


class ComprobanteService:

    @staticmethod
    def emitir(
        pago: Pago,
        tipo: str,
        serie: str,
        numero: int,
        cliente_nombre: str = "",
        cliente_ruc_dni: str = "",
        cliente_direccion: str = "",
    ) -> Comprobante:

        if hasattr(pago, "comprobante"):
            raise ValueError("Este pago ya tiene un comprobante emitido.")

        if tipo == Comprobante.TipoComprobante.FACTURA:
            if not cliente_nombre or not cliente_ruc_dni:
                raise ValueError("Para emitir una factura se requiere nombre y RUC del cliente.")

        return Comprobante.objects.create(
            pago=pago,
            tipo=tipo,
            serie=serie,
            numero=numero,
            cliente_nombre=cliente_nombre,
            cliente_ruc_dni=cliente_ruc_dni,
            cliente_direccion=cliente_direccion,
        )
