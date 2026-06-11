from rest_framework import serializers

from memos_cafe.ordenes.models import DetalleOrden, Orden
from memos_cafe.productos.api.serializers import ProductoSerializer, PromocionSerializer


class DetalleOrdenReadSerializer(serializers.ModelSerializer):
    """Lectura: producto y promoción anidados completos."""
    producto = ProductoSerializer(read_only=True)
    promocion = PromocionSerializer(read_only=True)

    class Meta:
        model = DetalleOrden
        fields = [
            "id",
            "producto",
            "promocion",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "nota",
            "impreso",
        ]


class DetalleOrdenWriteSerializer(serializers.Serializer):
    """Valida un ítem al crear o agregar a una orden."""
    producto = serializers.PrimaryKeyRelatedField(
        queryset=__import__(
            "memos_cafe.productos.models", fromlist=["Producto"]
        ).Producto.objects.filter(disponible=True),
        required=False,
        allow_null=True,
    )
    promocion = serializers.PrimaryKeyRelatedField(
        queryset=__import__(
            "memos_cafe.productos.models", fromlist=["Promocion"]
        ).Promocion.objects.filter(activo=True),
        required=False,
        allow_null=True,
    )
    cantidad = serializers.IntegerField(min_value=1)
    nota = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")

    def validate(self, data):
        if not data.get("producto") and not data.get("promocion"):
            raise serializers.ValidationError(
                "Debe especificar al menos un producto o una promoción."
            )
        return data


class OrdenReadSerializer(serializers.ModelSerializer):
    """Lectura completa de una orden con detalles anidados."""
    detalles = DetalleOrdenReadSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(
        source="usuario.get_full_name", read_only=True
    )
    mesa_numero = serializers.IntegerField(
        source="mesa.numero", read_only=True, default=None
    )
    estado_display = serializers.CharField(
        source="get_estado_display", read_only=True
    )
    tipo_orden_display = serializers.CharField(
        source="get_tipo_orden_display", read_only=True
    )

    class Meta:
        model = Orden
        fields = [
            "id",
            "mesa",
            "mesa_numero",
            "usuario",
            "usuario_nombre",
            "estado",
            "estado_display",
            "tipo_orden",
            "tipo_orden_display",
            "fecha_creacion",
            "fecha_cierre",
            "total",
            "detalles",
        ]


class OrdenWriteSerializer(serializers.Serializer):
    """Valida datos para crear una orden con sus ítems."""
    mesa = serializers.PrimaryKeyRelatedField(
        queryset=__import__(
            "memos_cafe.mesas.models", fromlist=["Mesa"]
        ).Mesa.objects.filter(activo=True),
        required=False,
        allow_null=True,
    )
    tipo_orden = serializers.ChoiceField(choices=Orden.TipoOrden.choices)
    detalles = DetalleOrdenWriteSerializer(many=True)

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError(
                "La orden debe tener al menos un ítem."
            )
        return value

    def validate(self, data):
        tipo_orden = data.get("tipo_orden")
        mesa = data.get("mesa")
        if tipo_orden == Orden.TipoOrden.MESA and not mesa:
            raise serializers.ValidationError(
                {"mesa": "Debe asignar una mesa para órdenes de tipo 'mesa'."}
            )
        return data


class MarcarImpresoSerializer(serializers.Serializer):
    """Valida los ids de detalle a marcar como enviados a cocina/barra."""
    detalle_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )