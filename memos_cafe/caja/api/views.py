from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins

from memos_cafe.caja.models import Caja
from memos_cafe.caja.models import Comprobante
from memos_cafe.caja.models import MovimientoCaja
from memos_cafe.caja.models import Pago
from memos_cafe.caja.api.serializers import AbrirCajaSerializer
from memos_cafe.caja.api.serializers import CajaReadSerializer
from memos_cafe.caja.api.serializers import CerrarCajaSerializer
from memos_cafe.caja.api.serializers import ComprobanteSerializer
from memos_cafe.caja.api.serializers import MovimientoCajaSerializer
from memos_cafe.caja.api.serializers import PagoReadSerializer
from memos_cafe.caja.api.serializers import PagoWriteSerializer
from memos_cafe.utils.permissions import EsAdmin
from memos_cafe.utils.permissions import EsAdminOCajero


class CajaViewSet(GenericViewSet):
    """
    estado:  GET  /api/caja/estado/  → admin o cajero
    abrir:   POST /api/caja/abrir/   → admin o cajero
    cerrar:  POST /api/caja/cerrar/  → admin o cajero
    """
    permission_classes = [EsAdminOCajero]
    queryset = Caja.objects.all()

    @action(detail=False, methods=["get"], url_path="estado")
    def estado(self, request):
        """GET /api/caja/estado/ — devuelve la sesión actualmente abierta."""
        caja = Caja.get_sesion_abierta()
        if not caja:
            return Response(
                {"detail": "No hay ninguna sesión de caja abierta."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CajaReadSerializer(caja).data)

    @action(detail=False, methods=["post"], url_path="abrir")
    def abrir(self, request):
        """POST /api/caja/abrir/ — abre una nueva sesión de caja."""
        serializer = AbrirCajaSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        caja = serializer.save()
        return Response(CajaReadSerializer(caja).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="cerrar")
    def cerrar(self, request):
        """POST /api/caja/cerrar/ — cierra la sesión activa."""
        caja = Caja.get_sesion_abierta()
        if not caja:
            return Response(
                {"detail": "No hay ninguna sesión de caja abierta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CerrarCajaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        caja.cerrar(
            monto_final=serializer.validated_data["monto_final"],
            observaciones=serializer.validated_data.get("observaciones", ""),
        )
        return Response(CajaReadSerializer(caja).data)


class MovimientoCajaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    list:   GET  /api/movimientos/  → admin o cajero
    create: POST /api/movimientos/  → admin o cajero
    """
    serializer_class = MovimientoCajaSerializer
    permission_classes = [EsAdminOCajero]

    def get_queryset(self):
        caja = Caja.get_sesion_abierta()
        if not caja:
            return MovimientoCaja.objects.none()
        return caja.movimientos.all()


class PagoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    list:    GET  /api/pagos/      → admin o cajero
    create:  POST /api/pagos/      → admin o cajero
    retrieve:GET  /api/pagos/{id}/ → admin o cajero
    anular:  POST /api/pagos/{id}/anular/ → solo admin
    """
    permission_classes = [EsAdminOCajero]

    def get_queryset(self):
        return Pago.objects.select_related("orden", "caja").all()

    def get_serializer_class(self):
        if self.action == "create":
            return PagoWriteSerializer
        return PagoReadSerializer

    @action(detail=True, methods=["post"], url_path="anular", permission_classes=[EsAdmin])
    def anular(self, request, pk=None):
        """POST /api/pagos/{id}/anular/ — solo admin."""
        pago = self.get_object()
        try:
            pago.anular()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PagoReadSerializer(pago).data)


class ComprobanteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    list:    GET  /api/comprobantes/      → admin o cajero
    create:  POST /api/comprobantes/      → admin o cajero
    retrieve:GET  /api/comprobantes/{id}/ → admin o cajero
    """
    serializer_class = ComprobanteSerializer
    permission_classes = [EsAdminOCajero]
    queryset = Comprobante.objects.select_related("pago").all()