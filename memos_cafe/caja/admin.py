from django.contrib import admin

from memos_cafe.caja.models import Caja, Comprobante, MovimientoCaja, Pago


class MovimientoCajaInline(admin.TabularInline):
    model = MovimientoCaja
    extra = 0
    readonly_fields = ["fecha"]
    fields = ["tipo", "monto", "motivo", "fecha"]


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    readonly_fields = ["orden", "metodo_pago", "monto", "vuelto", "estado", "fecha"]
    fields = ["orden", "metodo_pago", "monto", "vuelto", "estado", "fecha"]
    can_delete = False


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ["id", "usuario", "estado", "monto_inicial", "monto_final", "fecha_apertura", "fecha_cierre"]
    list_filter = ["estado", "fecha_apertura"]
    search_fields = ["usuario__email"]
    ordering = ["-fecha_apertura"]
    readonly_fields = ["fecha_apertura", "fecha_cierre"]
    list_select_related = ["usuario"]
    inlines = [MovimientoCajaInline, PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ["id", "orden", "caja", "metodo_pago", "monto", "vuelto", "estado", "fecha"]
    list_filter = ["estado", "metodo_pago", "fecha"]
    search_fields = ["orden__id", "caja__id"]
    ordering = ["-fecha"]
    readonly_fields = ["fecha"]
    list_select_related = ["orden", "caja"]


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ["id", "caja", "tipo", "monto", "motivo", "fecha"]
    list_filter = ["tipo", "fecha"]
    search_fields = ["motivo", "caja__id"]
    ordering = ["-fecha"]
    readonly_fields = ["fecha"]
    list_select_related = ["caja"]


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "tipo", "pago", "cliente_nombre", "cliente_ruc_dni", "fecha_emision"]
    list_filter = ["tipo", "fecha_emision"]
    search_fields = ["serie", "numero", "cliente_nombre", "cliente_ruc_dni"]
    ordering = ["-fecha_emision"]
    readonly_fields = ["fecha_emision"]
    list_select_related = ["pago"]