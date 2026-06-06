from django.contrib import admin
from memos_cafe.roles.models import PermisoRol


@admin.register(PermisoRol)
class PermisoRolAdmin(admin.ModelAdmin):
    list_display  = ["modulo", "rol", "puede_acceder"]
    list_filter   = ["rol", "modulo"]
    list_editable = ["puede_acceder"]
