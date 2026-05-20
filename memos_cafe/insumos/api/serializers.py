from rest_framework import serializers

from memos_cafe.insumos.models import RegistroInsumo
from memos_cafe.insumos.models import TipoInsumo


class TipoInsumoSerializer(serializers.ModelSerializer):
    stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = TipoInsumo
        fields = [
            "id",
            "nombre",
            "unidad",
            "stock_minimo",
            "stock_actual",
            "stock_bajo",
            "activo",
        ]
        read_only_fields = ["stock_actual"]

    def validate_stock_minimo(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo.")
        return value


class RegistroInsumoSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    insumo_unidad = serializers.CharField(source="insumo.unidad", read_only=True)

    class Meta:
        model = RegistroInsumo
        fields = [
            "id",
            "insumo",
            "insumo_nombre",
            "insumo_unidad",
            "cantidad",
            "costo_unitario",
            "costo_total",
            "proveedor",
            "fecha",
            "observaciones",
        ]
        read_only_fields = ["costo_total", "fecha"]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def validate_costo_unitario(self, value):
        if value <= 0:
            raise serializers.ValidationError("El costo unitario debe ser mayor a 0.")
        return value

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)