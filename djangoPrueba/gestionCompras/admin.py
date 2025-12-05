from django.contrib import admin
from .models import Compra, DetalleCompra

# =====================================================
# INLINE DETALLE COMPRA
# =====================================================

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    fields = (
        "producto",
        "cantidad",
        "precio_unitario",
        "iva_porcentaje",
        "iva_monto",
        "subtotal",
        "subtotal_con_iva",
        "observacion",
    )
    readonly_fields = (
        "iva_porcentaje",
        "iva_monto",
        "subtotal",
        "subtotal_con_iva",
    )


# =====================================================
# ADMIN COMPRA
# =====================================================

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):

    list_display = (
        "idCompra",
        "proveedor",
        "fecha_compra",
        "metodo_pago",
        "estado",
        "total",
        "total_con_iva",
    )

    list_filter = ("proveedor", "metodo_pago", "estado", "fecha_compra")
    search_fields = ("proveedor__nombre", "idCompra")

    readonly_fields = (
        "total",
        "iva_total",
        "total_con_iva",
        "fecha_compra",
    )

    inlines = [DetalleCompraInline]

    fieldsets = (
        ("Datos de la compra", {
            "fields": (
                "proveedor",
                "fecha_compra",
                "metodo_pago",
                "observaciones",
            )
        }),
        ("Estado", {
            "fields": ("estado",),
        }),
        ("Totales", {
            "fields": ("total", "iva_total", "total_con_iva"),
        }),
    )

    # 🔒 Solo los administradores pueden editar el estado
    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)

        if not request.user.is_superuser:  # o request.user.is_staff si preferís
            ro.append("estado")

        return ro

    # Recalcular totales
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calcular_totales()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calcular_totales()



# =====================================================
# ADMIN DETALLE COMPRA
# =====================================================

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = (
        "idDetalleCompra",
        "compra",
        "producto",
        "cantidad",
        "precio_unitario",
        "iva_porcentaje",
        "iva_monto",
        "subtotal_con_iva",
    )
    readonly_fields = ("iva_porcentaje", "iva_monto", "subtotal_con_iva")
