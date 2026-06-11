from rest_framework import serializers

from memos_cafe.mesas.models import Mesa
from memos_cafe.ordenes.models import DetalleOrden, Orden
from memos_cafe.productos.api.serializers import ProductoSerializer, PromocionSerializer
from memos_cafe.productos.models import Producto, Promocion


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
        ]


class DetalleOrdenWriteSerializer(serializers.Serializer):
    """Valida un ítem al crear o agregar a una orden."""
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(disponible=True),
        required=False,
        allow_null=True,
    )
    promocion = serializers.PrimaryKeyRelatedField(
        queryset=Promocion.objects.filter(activo=True),
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
            "cliente_nombre",
            "cliente_telefono",
            "direccion_entrega",
            "plataforma_delivery",
            "plataforma_otra",
            "detalles",
        ]


class OrdenWriteSerializer(serializers.Serializer):
    """Valida datos para crear una orden con sus ítems."""
    mesa = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.filter(activo=True),
        required=False,
        allow_null=True,
    )
    tipo_orden = serializers.ChoiceField(choices=Orden.TipoOrden.choices)
    detalles = DetalleOrdenWriteSerializer(many=True)

    # Campos delivery (opcionales según tipo_orden)
    cliente_nombre = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    cliente_telefono = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    direccion_entrega = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    plataforma_delivery = serializers.ChoiceField(
        choices=Orden.PlataformaDelivery.choices,
        required=False,
        allow_null=True,
    )
    plataforma_otra = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")

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
        if tipo_orden == Orden.TipoOrden.DELIVERY:
            if not data.get("plataforma_delivery"):
                raise serializers.ValidationError(
                    {"plataforma_delivery": "Debe especificar la plataforma para órdenes delivery."}
                )
            plataforma = data.get("plataforma_delivery")
            if plataforma == Orden.PlataformaDelivery.OTRO and not data.get("plataforma_otra"):
                raise serializers.ValidationError(
                    {"plataforma_otra": "Debe especificar el nombre de la plataforma."}
                )
        return data
