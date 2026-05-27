from django.contrib import admin

from memos_cafe.ordenes.models import DetalleOrden, Orden


class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 0
    readonly_fields = ["subtotal"]
    fields = ["producto", "promocion", "cantidad", "precio_unitario", "subtotal", "nota"]


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ["id", "mesa", "usuario", "tipo_orden", "estado", "total", "fecha_creacion"]
    list_filter = ["estado", "tipo_orden", "fecha_creacion"]
    search_fields = ["id", "usuario__email", "mesa__numero"]
    ordering = ["-fecha_creacion"]
    readonly_fields = ["fecha_creacion", "fecha_cierre", "total"]
    list_select_related = ["mesa", "usuario"]
    inlines = [DetalleOrdenInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("mesa", "usuario")