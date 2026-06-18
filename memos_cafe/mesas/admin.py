from django.contrib import admin

from memos_cafe.mesas.models import Mesa


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ["numero", "capacidad", "estado", "activo", "fecha_baja"]
    list_filter = ["estado", "activo"]
    search_fields = ["numero"]
    ordering = ["numero"]
    readonly_fields = ["fecha_baja"]

    actions = ["marcar_libre", "dar_de_baja"]

    @admin.action(description="Marcar mesas seleccionadas como libres")
    def marcar_libre(self, request, queryset):
        queryset.update(estado=Mesa.Estado.LIBRE)

    @admin.action(description="Dar de baja mesas seleccionadas")
    def dar_de_baja(self, request, queryset):
        for mesa in queryset:
            mesa.dar_de_baja()