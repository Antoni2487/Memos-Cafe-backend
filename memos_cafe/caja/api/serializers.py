from rest_framework import serializers

from memos_cafe.caja.models import Caja
from memos_cafe.caja.models import Comprobante
from memos_cafe.caja.models import MovimientoCaja
from memos_cafe.caja.models import Pago
from memos_cafe.ordenes.api.serializers import OrdenReadSerializer


class AbrirCajaSerializer(serializers.ModelSerializer):
    """El cajero abre la sesión con un monto inicial."""

    class Meta:
        model = Caja
        fields = ["id", "monto_inicial"]

    def validate(self, data):
        if Caja.get_sesion_abierta():
            raise serializers.ValidationError(
                "Ya existe una sesión de caja abierta. Ciérrela antes de abrir una nueva."
            )
        return data

    def validate_monto_inicial(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto inicial no puede ser negativo.")
        return value

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class CerrarCajaSerializer(serializers.Serializer):
    """El cajero cierra la sesión con el monto contado."""
    monto_final = serializers.DecimalField(max_digits=10, decimal_places=2)
    observaciones = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_monto_final(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto final no puede ser negativo.")
        return value


class CajaReadSerializer(serializers.ModelSerializer):
    """Lectura del estado actual de la caja."""
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)
    total_ventas = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    diferencia = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

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


class MovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = ["id", "tipo", "monto", "motivo", "fecha"]
        read_only_fields = ["fecha"]

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value

    def create(self, validated_data):
        # La caja activa se asigna automáticamente
        caja = Caja.get_sesion_abierta()
        if not caja:
            raise serializers.ValidationError("No hay una sesión de caja abierta.")
        validated_data["caja"] = caja
        return super().create(validated_data)


class PagoReadSerializer(serializers.ModelSerializer):
    """Lectura: incluye la orden anidada."""
    orden = OrdenReadSerializer(read_only=True)

    class Meta:
        model = Pago
        fields = [
            "id",
            "orden",
            "caja",
            "metodo_pago",
            "monto",
            "vuelto",
            "estado",
            "fecha",
        ]


class PagoWriteSerializer(serializers.ModelSerializer):
    """El cajero registra el cobro de una orden."""

    class Meta:
        model = Pago
        fields = ["id", "orden", "metodo_pago", "monto"]

    def validate_orden(self, orden):
        if orden.estado != "abierta":
            raise serializers.ValidationError(
                "Solo se pueden cobrar órdenes abiertas."
            )
        if hasattr(orden, "pago"):
            raise serializers.ValidationError(
                "Esta orden ya tiene un pago registrado."
            )
        return orden

    def validate(self, data):
        orden = data.get("orden")
        monto = data.get("monto")
        if monto < orden.total:
            raise serializers.ValidationError(
                {"monto": f"El monto recibido (S/.{monto}) es menor al total de la orden (S/.{orden.total})."}
            )
        return data

    def create(self, validated_data):
        caja = Caja.get_sesion_abierta()
        if not caja:
            raise serializers.ValidationError("No hay una sesión de caja abierta.")
        orden = validated_data["orden"]
        monto = validated_data["monto"]
        vuelto = monto - orden.total
        pago = Pago.objects.create(
            caja=caja,
            vuelto=vuelto,
            **validated_data,
        )
        # Cierra la orden automáticamente al cobrar
        orden.cerrar()
        return pago


class ComprobanteSerializer(serializers.ModelSerializer):
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
        read_only_fields = ["fecha_emision"]

    def validate(self, data):
        tipo = data.get("tipo")
        # Si es factura, los datos del cliente son obligatorios
        if tipo == Comprobante.TipoComprobante.FACTURA:
            if not data.get("cliente_nombre"):
                raise serializers.ValidationError(
                    {"cliente_nombre": "Requerido para facturas."}
                )
            if not data.get("cliente_ruc_dni"):
                raise serializers.ValidationError(
                    {"cliente_ruc_dni": "Requerido para facturas."}
                )
        return data