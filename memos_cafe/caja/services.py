from decimal import Decimal

from django.db import transaction

from memos_cafe.caja.models import Caja, Comprobante, MovimientoCaja, Pago
from memos_cafe.ordenes.models import Orden


class CajaService:
    
    @staticmethod
    def abrir_sesion(usuario, monto_inicial: Decimal) -> Caja:
        """
        Abre una nueva sesión de caja.
        Lanza ValueError si ya hay una sesión abierta.
        """
        if Caja.objects.get_sesion_abierta():
            raise ValueError(
                "Ya existe una sesión de caja abierta. Ciérrela antes de abrir una nueva."
            )
        return Caja.objects.create(
            usuario=usuario,
            monto_inicial=monto_inicial,
        )

    @staticmethod
    def cerrar_sesion(monto_final: Decimal, observaciones: str = "") -> Caja:
        caja = Caja.objects.get_sesion_abierta_o_error()
        caja.cerrar(monto_final=monto_final, observaciones=observaciones)
        return caja

    @staticmethod
    def registrar_movimiento(tipo: str, monto: Decimal, motivo: str) -> MovimientoCaja:
    
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0.")
        caja = Caja.objects.get_sesion_abierta_o_error()
        return MovimientoCaja.objects.create(
            caja=caja,
            tipo=tipo,
            monto=monto,
            motivo=motivo,
        )


class PagoService:

    @staticmethod
    @transaction.atomic
    def procesar_pago(
        orden: Orden,
        metodo_pago: str,
        monto: Decimal,
    ) -> Pago:
        
        if orden.estado != Orden.Estado.ABIERTA:
            raise ValueError("Solo se pueden cobrar órdenes abiertas.")

        # Fix 11 — .exists() en lugar de hasattr para verificar pago existente
        if Pago.objects.filter(orden=orden).exists():
            raise ValueError("Esta orden ya tiene un pago registrado.")

        if monto < orden.total:
            raise ValueError(
                f"Monto insuficiente. "
                f"Total de la orden: S/.{orden.total}, "
                f"monto recibido: S/.{monto}."
            )

        caja = Caja.objects.get_sesion_abierta_o_error()
        vuelto = monto - orden.total

        pago = Pago.objects.create(
            orden=orden,
            caja=caja,
            metodo_pago=metodo_pago,
            monto=monto,
            vuelto=vuelto,
        )

        orden.cerrar()
        return pago

    @staticmethod
    @transaction.atomic
    def anular_pago(pago: Pago) -> Pago:
    
        if pago.estado == Pago.Estado.ANULADO:
            raise ValueError("Este pago ya está anulado.")

        orden = pago.orden
        if orden.estado == Orden.Estado.ANULADA:
            raise ValueError("La orden asociada a este pago ya está anulada.")

        pago.anular()

        orden.anular()

        # 3 — Registrar salida de caja por la devolución
        MovimientoCaja.objects.create(
            caja=pago.caja,
            tipo=MovimientoCaja.Tipo.SALIDA,
            monto=pago.monto,
            motivo=f"Devolución por anulación de pago #{pago.id} — Orden #{orden.id}",
        )

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
                raise ValueError(
                    "Para emitir una factura se requiere nombre y RUC/DNI del cliente."
                )

        return Comprobante.objects.create(
            pago=pago,
            tipo=tipo,
            serie=serie,
            numero=numero,
            cliente_nombre=cliente_nombre,
            cliente_ruc_dni=cliente_ruc_dni,
            cliente_direccion=cliente_direccion,
        )