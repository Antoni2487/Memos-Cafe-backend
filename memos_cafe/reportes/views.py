from django.db.models import Count
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncDate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from memos_cafe.caja.models import Caja
from memos_cafe.caja.models import Pago
from memos_cafe.ordenes.models import DetalleOrden
from memos_cafe.utils.permissions import EsAdmin


class ReporteVentasView(APIView):
    """
    GET /api/reportes/ventas/
    Filtros: fecha_inicio, fecha_fin, usuario_id, metodo_pago
    Solo admin.
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        usuario_id = request.query_params.get("usuario_id")
        metodo_pago = request.query_params.get("metodo_pago")

        # Validaciones
        if not fecha_inicio or not fecha_fin:
            return Response(
                {"detail": "Los parámetros fecha_inicio y fecha_fin son requeridos."},
                status=400,
            )

        # Base queryset — solo pagos completados
        pagos = Pago.objects.filter(
            estado="completado",
            fecha__date__gte=fecha_inicio,
            fecha__date__lte=fecha_fin,
        )

        if usuario_id:
            pagos = pagos.filter(orden__usuario_id=usuario_id)
        if metodo_pago:
            pagos = pagos.filter(metodo_pago=metodo_pago)

        # Totales generales
        totales = pagos.aggregate(
            total_ventas=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
            total_ordenes=Count("id"),
        )
        total_ventas = totales["total_ventas"]
        total_ordenes = totales["total_ordenes"]
        ticket_promedio = (
            round(total_ventas / total_ordenes, 2) if total_ordenes > 0 else 0
        )

        # Ventas por día
        ventas_por_dia = (
            pagos.annotate(fecha=TruncDate("fecha"))
            .values("fecha")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                ordenes=Count("id"),
            )
            .order_by("fecha")
        )

        # Ventas por método de pago
        ventas_por_metodo = (
            pagos.values("metodo_pago")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                cantidad=Count("id"),
            )
            .order_by("-total")
        )

        return Response({
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin,
            },
            "filtros": {
                "usuario_id": usuario_id,
                "metodo_pago": metodo_pago,
            },
            "total_ventas": total_ventas,
            "total_ordenes": total_ordenes,
            "ticket_promedio": ticket_promedio,
            "ventas_por_dia": list(ventas_por_dia),
            "ventas_por_metodo_pago": list(ventas_por_metodo),
        })


class ReporteProductosView(APIView):
    """
    GET /api/reportes/productos/
    Filtros: fecha_inicio, fecha_fin, usuario_id, metodo_pago
    Solo admin.
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        usuario_id = request.query_params.get("usuario_id")
        metodo_pago = request.query_params.get("metodo_pago")

        if not fecha_inicio or not fecha_fin:
            return Response(
                {"detail": "Los parámetros fecha_inicio y fecha_fin son requeridos."},
                status=400,
            )

        # Filtra detalles de órdenes cerradas en el período
        detalles = DetalleOrden.objects.filter(
            orden__estado="cerrada",
            orden__fecha_cierre__date__gte=fecha_inicio,
            orden__fecha_cierre__date__lte=fecha_fin,
            producto__isnull=False,  # solo productos, no promociones
        )

        if usuario_id:
            detalles = detalles.filter(orden__usuario_id=usuario_id)
        if metodo_pago:
            detalles = detalles.filter(orden__pago__metodo_pago=metodo_pago)

        productos = (
            detalles.values(
                nombre=F("producto__nombre"),
                categoria=F("producto__categoria__nombre"),
            )
            .annotate(
                cantidad=Sum("cantidad"),
                total=Coalesce(Sum("subtotal"), Value(0), output_field=DecimalField()),
            )
            .order_by("-cantidad")
        )

        # Promociones más vendidas aparte
        detalles_promo = DetalleOrden.objects.filter(
            orden__estado="cerrada",
            orden__fecha_cierre__date__gte=fecha_inicio,
            orden__fecha_cierre__date__lte=fecha_fin,
            promocion__isnull=False,
        )
        if usuario_id:
            detalles_promo = detalles_promo.filter(orden__usuario_id=usuario_id)

        promociones = (
            detalles_promo.values(nombre=F("promocion__nombre"))
            .annotate(
                cantidad=Sum("cantidad"),
                total=Coalesce(Sum("subtotal"), Value(0), output_field=DecimalField()),
            )
            .order_by("-cantidad")
        )

        return Response({
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin,
            },
            "productos": list(productos),
            "promociones": list(promociones),
        })


class ReporteCajaView(APIView):
    """
    GET /api/reportes/caja/
    Filtros: fecha_inicio, fecha_fin, usuario_id, metodo_pago
    También acepta caja_id para el cuadre de un turno específico.
    Solo admin.
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        usuario_id = request.query_params.get("usuario_id")
        metodo_pago = request.query_params.get("metodo_pago")
        caja_id = request.query_params.get("caja_id")

        # Si piden un turno específico
        if caja_id:
            try:
                caja = Caja.objects.get(id=caja_id)
            except Caja.DoesNotExist:
                return Response({"detail": "Sesión de caja no encontrada."}, status=404)
            return Response(self._cuadre_caja(caja, metodo_pago))

        # Si piden un rango de fechas
        if not fecha_inicio or not fecha_fin:
            return Response(
                {"detail": "Debe enviar caja_id o fecha_inicio y fecha_fin."},
                status=400,
            )

        cajas = Caja.objects.filter(
            estado="cerrada",
            fecha_apertura__date__gte=fecha_inicio,
            fecha_cierre__date__lte=fecha_fin,
        )
        if usuario_id:
            cajas = cajas.filter(usuario_id=usuario_id)

        return Response({
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "turnos": [self._cuadre_caja(c, metodo_pago) for c in cajas],
        })

    def _cuadre_caja(self, caja, metodo_pago=None):
        """Arma el resumen de un turno de caja."""
        pagos = caja.pagos.filter(estado="completado")
        if metodo_pago:
            pagos = pagos.filter(metodo_pago=metodo_pago)

        totales = pagos.aggregate(
            total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField())
        )

        # Desglose por método de pago
        por_metodo = (
            pagos.values("metodo_pago")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField())
            )
        )
        metodos = {item["metodo_pago"]: item["total"] for item in por_metodo}

        total_ventas = totales["total"]
        monto_inicial = caja.monto_inicial or 0
        monto_final_esperado = monto_inicial + total_ventas
        monto_final_contado = caja.monto_final or 0
        diferencia = (
            monto_final_contado - monto_final_esperado
            if caja.monto_final is not None
            else None
        )

        return {
            "caja_id": caja.id,
            "cajero": caja.usuario.get_full_name() or caja.usuario.email,
            "estado": caja.estado,
            "fecha_apertura": caja.fecha_apertura,
            "fecha_cierre": caja.fecha_cierre,
            "monto_inicial": monto_inicial,
            "total_ventas": total_ventas,
            "desglose_metodos": metodos,
            "monto_final_esperado": monto_final_esperado,
            "monto_final_contado": monto_final_contado,
            "diferencia": diferencia,
            "observaciones": caja.observaciones,
        }