from rest_framework import serializers

from memos_cafe.caja.models import Caja, Comprobante, MovimientoCaja, Pago
from memos_cafe.ordenes.api.serializers import OrdenReadSerializer
from memos_cafe.ordenes.models import Orden  # fix 3: import directo, sin __import__


class AbrirCajaSerializer(serializers.Serializer):
    """Valida los datos para abrir una sesión de caja."""
    monto_inicial = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_monto_inicial(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto inicial no puede ser negativo.")
        return value


class CerrarCajaSerializer(serializers.Serializer):
    """Valida los datos para cerrar una sesión de caja."""
    monto_final = serializers.DecimalField(max_digits=10, decimal_places=2)
    observaciones = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_monto_final(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto final no puede ser negativo.")
        return value


class CajaReadSerializer(serializers.ModelSerializer):
    """Representación completa de una sesión de caja."""
    usuario_nombre = serializers.CharField(
        source="usuario.get_full_name", read_only=True
    )
    total_ventas = serializers.SerializerMethodField()
    movimientos_neto = serializers.SerializerMethodField()
    esperado_en_caja = serializers.SerializerMethodField()
    diferencia = serializers.SerializerMethodField()

    class Meta:
        model = Caja
        fields = [
            "id",
            "usuario",
            "usuario_nombre",
            "estado",
            "monto_inicial",
            "monto_final",
            "total_ventas",
            "movimientos_neto",
            "esperado_en_caja",
            "diferencia",
            "fecha_apertura",
            "fecha_cierre",
            "observaciones",
        ]

    def _get_total_ventas(self, obj):
        """
        Fix 9: calcula total_por_caja una sola vez y lo cachea en el objeto
        durante la serialización. Antes se llamaba dos veces (get_total_ventas
        + get_diferencia) = 2 queries por objeto en el listado.
        Ahora = 1 query por objeto.
        """
        cache_attr = "_total_ventas_cache"
        if not hasattr(obj, cache_attr):
            resultado = Pago.objects.total_por_caja(obj)
            setattr(obj, cache_attr, resultado["total"])
        return getattr(obj, cache_attr)

    def _get_movimientos_neto(self, obj):
        """Entradas menos salidas de movimientos manuales, cacheado
        igual que total_ventas para no duplicar queries."""
        cache_attr = "_movimientos_neto_cache"
        if not hasattr(obj, cache_attr):
            neto = MovimientoCaja.objects.neto_por_caja(obj)
            setattr(obj, cache_attr, neto)
        return getattr(obj, cache_attr)

    def get_total_ventas(self, obj):
        return self._get_total_ventas(obj)

    def get_movimientos_neto(self, obj):
        return self._get_movimientos_neto(obj)

    def get_esperado_en_caja(self, obj):
        """Lo que deberia haber fisicamente en caja: fondo inicial +
        ventas + movimientos manuales (entradas suman, salidas restan)."""
        ventas = self._get_total_ventas(obj)
        neto_mov = self._get_movimientos_neto(obj)
        return obj.monto_inicial + ventas + neto_mov

    def get_diferencia(self, obj):
        if obj.monto_final is None:
            return None
        esperado = self.get_esperado_en_caja(obj)
        return obj.monto_final - esperado


class MovimientoCajaSerializer(serializers.Serializer):
    """Valida datos para registrar un movimiento de caja."""
    tipo = serializers.ChoiceField(choices=MovimientoCaja.Tipo.choices)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    motivo = serializers.CharField(max_length=200)

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value


class MovimientoCajaReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = ["id", "tipo", "monto", "motivo", "fecha"]



class PagoWriteSerializer(serializers.Serializer):
    orden = serializers.PrimaryKeyRelatedField(
        queryset=Orden.objects.filter(estado="abierta")
    )
    metodo_pago = serializers.ChoiceField(choices=Pago.MetodoPago.choices)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    monto_recibido = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    numero_operacion = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value


class PagoReadSerializer(serializers.ModelSerializer):
    orden = OrdenReadSerializer(read_only=True)
    metodo_pago_display = serializers.CharField(
        source="get_metodo_pago_display", read_only=True
    )
    comprobante = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            "id",
            "orden",
            "caja",
            "metodo_pago",
            "metodo_pago_display",
            "monto",
            "monto_recibido",
            "vuelto",
            "numero_operacion",
            "estado",
            "fecha",
            "comprobante",
        ]

    def get_comprobante(self, obj):
        if hasattr(obj, "comprobante"):
            from memos_cafe.caja.api.serializers import ComprobanteReadSerializer
            return ComprobanteReadSerializer(obj.comprobante).data
        return None


class ComprobanteWriteSerializer(serializers.Serializer):
    """Valida datos para emitir un comprobante."""
    pago = serializers.PrimaryKeyRelatedField(
        queryset=Pago.objects.filter(estado="completado")
    )
    tipo = serializers.ChoiceField(choices=Comprobante.TipoComprobante.choices)
    serie = serializers.CharField(max_length=10)
    numero = serializers.IntegerField(min_value=1)
    cliente_nombre = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    cliente_ruc_dni = serializers.CharField(max_length=11, required=False, allow_blank=True, default="")
    cliente_direccion = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class ComprobanteReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = [
            "id",
            "pago",
            "tipo",
            "serie",
            "numero",
            "cliente_nombre",
            "cliente_ruc_dni",
            "cliente_direccion",
            "fecha_emision",
        ]
