from rest_framework import serializers

from memos_cafe.ordenes.models import DetalleOrden
from memos_cafe.ordenes.models import Orden
from memos_cafe.productos.api.serializers import ProductoSerializer
from memos_cafe.productos.api.serializers import PromocionSerializer


class DetalleOrdenReadSerializer(serializers.ModelSerializer):
    """Lectura: devuelve el producto y/o promoción completos (anidados)."""
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


class DetalleOrdenWriteSerializer(serializers.ModelSerializer):
    """Escritura: acepta IDs de producto y/o promoción."""

    class Meta:
        model = DetalleOrden
        fields = [
            "id",
            "producto",
            "promocion",
            "cantidad",
            "nota",
        ]

    def validate(self, data):
        producto = data.get("producto")
        promocion = data.get("promocion")
        if not producto and not promocion:
            raise serializers.ValidationError(
                "Debe especificar al menos un producto o una promoción."
            )
        return data

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def create(self, validated_data):
        """Calcula el precio_unitario automáticamente según producto o promoción."""
        producto = validated_data.get("producto")
        promocion = validated_data.get("promocion")

        # Si hay producto y promoción, el precio base es la suma de ambos
        precio = 0
        if producto:
            precio += producto.precio
        if promocion:
            precio += promocion.precio

        validated_data["precio_unitario"] = precio
        return super().create(validated_data)


class OrdenReadSerializer(serializers.ModelSerializer):
    """Lectura: devuelve los detalles completos anidados."""
    detalles = DetalleOrdenReadSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)
    mesa_numero = serializers.IntegerField(source="mesa.numero", read_only=True)

    class Meta:
        model = Orden
        fields = [
            "id",
            "mesa",
            "mesa_numero",
            "usuario",
            "usuario_nombre",
            "estado",
            "tipo_orden",
            "fecha_creacion",
            "fecha_cierre",
            "total",
            "detalles",
        ]


class OrdenWriteSerializer(serializers.ModelSerializer):
    """Escritura: crea una orden con sus detalles en una sola llamada."""
    detalles = DetalleOrdenWriteSerializer(many=True)

    class Meta:
        model = Orden
        fields = [
            "id",
            "mesa",
            "tipo_orden",
            "detalles",
        ]

    def validate(self, data):
        tipo_orden = data.get("tipo_orden")
        mesa = data.get("mesa")
        if tipo_orden == Orden.TipoOrden.MESA and not mesa:
            raise serializers.ValidationError(
                {"mesa": "Debe asignar una mesa para órdenes de tipo 'mesa'."}
            )
        if mesa and mesa.estado != "libre":
            raise serializers.ValidationError(
                {"mesa": f"La mesa {mesa.numero} no está libre."}
            )
        if not data.get("detalles"):
            raise serializers.ValidationError(
                {"detalles": "La orden debe tener al menos un detalle."}
            )
        return data

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles")
        # El usuario viene del request, no del body
        usuario = self.context["request"].user
        orden = Orden.objects.create(usuario=usuario, **validated_data)
        # Si tiene mesa, la marcamos como ocupada
        if orden.mesa:
            orden.mesa.ocupar()
        # Creamos cada detalle usando su propio serializer
        detalle_serializer = DetalleOrdenWriteSerializer()
        for detalle_data in detalles_data:
            detalle_data["orden"] = orden
            detalle_serializer.create(detalle_data)
        orden.refresh_from_db()
        return orden