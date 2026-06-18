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
            "diferencia",
            "fecha_apertura",
            "fecha_cierre",
            "observaciones",
        ]

    def _get_total_ventas(self, obj) -> object:
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

    def get_total_ventas(self, obj):
        return self._get_total_ventas(obj)

    def get_diferencia(self, obj):
        if obj.monto_final is None:
            return None
        total = self._get_total_ventas(obj)  # reutiliza el cache, sin query extra
        return obj.monto_final - (obj.monto_inicial + total)


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
    """Valida los datos para procesar un pago. Sin lógica de negocio."""
    # Fix 3: import directo arriba del archivo — sin __import__ hack.
    # El queryset se evalúa en cada request gracias al callable form.
    orden = serializers.PrimaryKeyRelatedField(
        queryset=Orden.objects.filter(estado="abierta")
    )
    metodo_pago = serializers.ChoiceField(choices=Pago.MetodoPago.choices)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value


class PagoReadSerializer(serializers.ModelSerializer):
    orden = OrdenReadSerializer(read_only=True)
    metodo_pago_display = serializers.CharField(
        source="get_metodo_pago_display", read_only=True
    )

    class Meta:
        model = Pago
        fields = [
            "id",
            "orden",
            "caja",
            "metodo_pago",
            "metodo_pago_display",
            "monto",
            "vuelto",
            "estado",
            "fecha",
        ]


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