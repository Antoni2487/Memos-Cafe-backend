from rest_framework import serializers
from memos_cafe.roles.models import PermisoRol


class PermisoRolSerializer(serializers.ModelSerializer):
    modulo_label = serializers.CharField(source="get_modulo_display", read_only=True)
    rol_label    = serializers.CharField(source="get_rol_display",    read_only=True)

    class Meta:
        model  = PermisoRol
        fields = ["id", "modulo", "modulo_label", "rol", "rol_label", "puede_acceder"]
        read_only_fields = ["id", "modulo", "rol", "modulo_label", "rol_label"]
