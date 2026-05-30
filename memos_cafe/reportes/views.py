from django.db.models import Count
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from memos_cafe.caja.models import Caja
from memos_cafe.caja.models import Pago
from memos_cafe.mesas.models import Mesa
from memos_cafe.ordenes.models import DetalleOrden
from memos_cafe.ordenes.models import Orden
from memos_cafe.utils.permissions import EsAdmin, EsAdminOCajero


class DashboardView(APIView):
    """
    GET /api/dashboard/
    KPIs del día actual para el admin.
    Solo admin.
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        hoy = timezone.localdate()

        # ── Órdenes ──────────────────────────────────────────────────────────
        ordenes_hoy = Orden.objects.filter(fecha_creacion__date=hoy)
        ordenes_abiertas = Orden.objects.filter(estado="abierta").count()
        ordenes_cerradas_hoy = ordenes_hoy.filter(estado="cerrada").count()
        ordenes_anuladas_hoy = ordenes_hoy.filter(estado="anulada").count()

        # ── Ventas del día ────────────────────────────────────────────────────
        pagos_hoy = Pago.objects.filter(
            estado="completado",
            fecha__date=hoy,
        )
        totales = pagos_hoy.aggregate(
            total_ventas=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
            total_pagos=Count("id"),
        )
        total_ventas = totales["total_ventas"]
        total_pagos = totales["total_pagos"]
        ticket_promedio = (
            round(total_ventas / total_pagos, 2) if total_pagos > 0 else 0
        )

        # Desglose por método de pago
        ventas_por_metodo = list(
            pagos_hoy.values("metodo_pago")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                cantidad=Count("id"),
            )
            .order_by("-total")
        )

        # ── Mesas ─────────────────────────────────────────────────────────────
        mesas = Mesa.objects.filter(activo=True)
        resumen_mesas = {
            "total": mesas.count(),
            "libres": mesas.filter(estado="libre").count(),
            "ocupadas": mesas.filter(estado="ocupada").count(),
            "reservadas": mesas.filter(estado="reservada").count(),
        }

        # ── Caja activa ───────────────────────────────────────────────────────
        caja_activa = Caja.objects.get_sesion_abierta()
        caja_info = None
        if caja_activa:
            pagos_caja = caja_activa.pagos.filter(estado="completado")
            ventas_turno = pagos_caja.aggregate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField())
            )["total"]
            caja_info = {
                "id": caja_activa.id,
                "cajero": caja_activa.usuario.get_full_name() or caja_activa.usuario.email,
                "fecha_apertura": caja_activa.fecha_apertura,
                "monto_inicial": caja_activa.monto_inicial,
                "ventas_turno": ventas_turno,
            }

        # ── Top 5 productos del día ───────────────────────────────────────────
        top_productos = list(
            DetalleOrden.objects.filter(
                orden__estado="cerrada",
                orden__fecha_cierre__date=hoy,
                producto__isnull=False,
            )
            .values(nombre=F("producto__nombre"))
            .annotate(cantidad=Sum("cantidad"))
            .order_by("-cantidad")[:5]
        )

        return Response({
            "fecha": hoy,
            "ordenes": {
                "abiertas": ordenes_abiertas,
                "cerradas_hoy": ordenes_cerradas_hoy,
                "anuladas_hoy": ordenes_anuladas_hoy,
            },
            "ventas": {
                "total": total_ventas,
                "ticket_promedio": ticket_promedio,
                "por_metodo": ventas_por_metodo,
            },
            "mesas": resumen_mesas,
            "caja_activa": caja_info,
            "top_productos": top_productos,
        })


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
        ventas_por_dia = list(
            pagos.annotate(fecha=TruncDate("fecha"))
            .values("fecha")
            .annotate(
                total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
                ordenes=Count("id"),
            )
            .order_by("fecha")
        )

        # Ventas por método de pago
        ventas_por_metodo = list(
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
            "ventas_por_dia": ventas_por_dia,
            "ventas_por_metodo_pago": ventas_por_metodo,
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
            producto__isnull=False,
        )

        if usuario_id:
            detalles = detalles.filter(orden__usuario_id=usuario_id)
        if metodo_pago:
            detalles = detalles.filter(orden__pago__metodo_pago=metodo_pago)

        productos = list(
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

        promociones = list(
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
            "productos": productos,
            "promociones": promociones,
        })


class ReporteCajaView(APIView):
    """
    GET /api/reportes/caja/
    Filtros: fecha_inicio, fecha_fin, usuario_id, metodo_pago, caja_id

    - Admin: ve todos los turnos o por rango de fechas
    - Cajero: solo puede ver su propio turno activo (via caja_id)
    """
    permission_classes = [EsAdminOCajero]

    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin    = request.query_params.get("fecha_fin")
        usuario_id   = request.query_params.get("usuario_id")
        metodo_pago  = request.query_params.get("metodo_pago")
        caja_id      = request.query_params.get("caja_id")
        es_admin     = request.user.groups.filter(name="admin").exists()

        # ── Turno específico por caja_id ──────────────────────────────────────
        if caja_id:
            try:
                caja = Caja.objects.get(id=caja_id)
            except Caja.DoesNotExist:
                return Response(
                    {"detail": "Sesión de caja no encontrada."},
                    status=404,
                )
            # Cajero solo puede ver sus propias cajas
            if not es_admin and caja.usuario != request.user:
                return Response(
                    {"detail": "No tienes permiso para ver esta sesión."},
                    status=403,
                )
            return Response(self._cuadre_caja(caja, metodo_pago))

        # ── Solo admin puede ver por rango de fechas ──────────────────────────
        if not es_admin:
            return Response(
                {"detail": "No tienes permiso para ver este reporte."},
                status=403,
            )

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
        """Arma el resumen completo de un turno de caja."""
        pagos = caja.pagos.filter(estado="completado")
        if metodo_pago:
            pagos = pagos.filter(metodo_pago=metodo_pago)

        totales = pagos.aggregate(
            total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
            cantidad_pagos=Count("id"),
        )

        # Desglose por método de pago
        por_metodo = pagos.values("metodo_pago").annotate(
            total=Coalesce(Sum("monto"), Value(0), output_field=DecimalField()),
            cantidad=Count("id"),
        )
        metodos = {item["metodo_pago"]: item["total"] for item in por_metodo}

        total_ventas          = totales["total"]
        monto_inicial         = caja.monto_inicial or 0
        monto_final_esperado  = monto_inicial + total_ventas
        monto_final_contado   = caja.monto_final or 0
        diferencia            = (
            monto_final_contado - monto_final_esperado
            if caja.monto_final is not None
            else None
        )

        return {
            "caja_id":              caja.id,
            "cajero":               caja.usuario.get_full_name() or caja.usuario.email,
            "estado":               caja.estado,
            "fecha_apertura":       caja.fecha_apertura,
            "fecha_cierre":         caja.fecha_cierre,
            "monto_inicial":        monto_inicial,
            "total_ventas":         total_ventas,
            "cantidad_pagos":       totales["cantidad_pagos"],
            "desglose_metodos":     metodos,
            "monto_final_esperado": monto_final_esperado,
            "monto_final_contado":  monto_final_contado,
            "diferencia":           diferencia,
            "observaciones":        caja.observaciones,
        }