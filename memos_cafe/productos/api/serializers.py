from rest_framework import serializers

from memos_cafe.productos.models import Categoria
from memos_cafe.productos.models import Producto
from memos_cafe.productos.models import Promocion


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "activo"]


class ProductoSerializer(serializers.ModelSerializer):
    """Lectura: incluye el nombre de la categoría."""
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "categoria",
            "categoria_nombre",
            "disponible",
            "imagen_url",
        ]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value


class ProductoWriteSerializer(serializers.ModelSerializer):
    """Escritura: solo acepta el ID de la categoría."""

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "categoria",
            "disponible",
            "imagen_url",
        ]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value


class PromocionSerializer(serializers.ModelSerializer):
    vigente = serializers.SerializerMethodField()

    class Meta:
        model = Promocion
        fields = [
            "id",
            "nombre",
            "descripcion",
            "imagen_url",
            "precio",
            "activo",
            "fecha_inicio",
            "fecha_fin",
            "vigente",
        ]

    def get_vigente(self, obj):
        return obj.esta_vigente()

    def validate(self, data):
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la de inicio."}
            )
        return data

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value