from django.contrib import admin

from memos_cafe.insumos.models import RegistroInsumo, TipoInsumo


class RegistroInsumoInline(admin.TabularInline):
    model = RegistroInsumo
    extra = 0
    readonly_fields = ["costo_total", "fecha"]
    fields = ["usuario", "cantidad", "costo_unitario", "costo_total", "proveedor", "fecha", "observaciones"]
    ordering = ["-fecha"]


@admin.register(TipoInsumo)
class TipoInsumoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "unidad", "stock_actual", "stock_minimo", "bajo_stock", "activo"]
    list_filter = ["activo", "unidad"]
    search_fields = ["nombre"]
    ordering = ["nombre"]
    readonly_fields = ["stock_actual"]
    inlines = [RegistroInsumoInline]

    @admin.display(description="Stock bajo", boolean=True)
    def bajo_stock(self, obj):
        return obj.stock_bajo


@admin.register(RegistroInsumo)
class RegistroInsumoAdmin(admin.ModelAdmin):
    list_display = ["insumo", "cantidad", "costo_unitario", "costo_total", "proveedor", "usuario", "fecha"]
    list_filter = ["fecha", "insumo"]
    search_fields = ["insumo__nombre", "proveedor", "usuario__email"]
    ordering = ["-fecha"]
    readonly_fields = ["costo_total", "fecha"]
    list_select_related = ["insumo", "usuario"]