from rest_framework import serializers

from memos_cafe.productos.models import Categoria, Producto, Promocion


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "activo"]


class ProductoSerializer(serializers.ModelSerializer):
    """Lectura — incluye nombre de categoría."""
    categoria_nombre = serializers.CharField(
        source="categoria.nombre", read_only=True
    )

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


class ProductoWriteSerializer(serializers.Serializer):
    """Escritura — valida datos para crear o actualizar un producto."""
    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.filter(activo=True)
    )
    disponible = serializers.BooleanField(default=True)
    imagen_url = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )

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


class PromocionWriteSerializer(serializers.Serializer):
    """Escritura — valida datos para crear o actualizar una promoción."""
    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    imagen_url = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate(self, data):
        if data.get("fecha_fin") and data.get("fecha_inicio"):
            if data["fecha_fin"] < data["fecha_inicio"]:
                raise serializers.ValidationError(
                    {"fecha_fin": "La fecha de fin no puede ser anterior a la de inicio."}
                )
        return data