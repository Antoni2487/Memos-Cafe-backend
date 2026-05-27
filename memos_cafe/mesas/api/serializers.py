from rest_framework import serializers

from memos_cafe.mesas.models import Mesa


class MesaSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(
        source="get_estado_display", read_only=True
    )

    class Meta:
        model = Mesa
        fields = [
            "id",
            "numero",
            "capacidad",
            "estado",
            "estado_display",
            "activo",
            "fecha_baja",
        ]
        read_only_fields = ["estado", "fecha_baja"]


class MesaWriteSerializer(serializers.Serializer):
    """Valida datos para crear o actualizar una mesa."""
    numero = serializers.IntegerField(min_value=1)
    capacidad = serializers.IntegerField(min_value=1)


class MesaEstadoSerializer(serializers.Serializer):
    """Valida el cambio de estado de una mesa."""
    estado = serializers.ChoiceField(choices=Mesa.Estado.choices)