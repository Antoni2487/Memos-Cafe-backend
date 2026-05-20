from rest_framework import serializers
from memos_cafe.mesas.models import Mesa


class MesaSerializer(serializers.ModelSerializer):
    """Lectura general de mesas (listado, detalle)."""

    class Meta:
        model = Mesa
        fields = [
            "id",
            "numero",
            "capacidad",
            "estado",
            "activo",
            "fecha_baja",
        ]
        read_only_fields = ["estado", "fecha_baja"]


class MesaEstadoSerializer(serializers.ModelSerializer):
    """Solo para cambiar el estado de una mesa (ocupar / liberar)."""

    class Meta:
        model = Mesa
        fields = ["estado"]

    def validate_estado(self, value):
        mesa = self.instance
        transiciones_validas = {
            Mesa.Estado.LIBRE: [Mesa.Estado.OCUPADA, Mesa.Estado.RESERVADA],
            Mesa.Estado.OCUPADA: [Mesa.Estado.LIBRE],
            Mesa.Estado.RESERVADA: [Mesa.Estado.LIBRE, Mesa.Estado.OCUPADA],
        }
        if value not in transiciones_validas.get(mesa.estado, []):
            raise serializers.ValidationError(
                f"No se puede pasar de '{mesa.estado}' a '{value}'."
            )
        return value