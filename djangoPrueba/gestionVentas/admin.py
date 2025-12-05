# gestionVentas/admin.py
from django.contrib import admin
from .models import Venta, DetalleVenta
from django import forms
from django.core.exceptions import PermissionDenied

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'iva_porcentaje', 'iva_monto', 'subtotal_con_iva', 'observacion')
    readonly_fields = ('iva_porcentaje', 'iva_monto', 'subtotal_con_iva')
    autocomplete_fields = ('producto',)

class VentaAdminForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = '__all__'
        readonly_fields = ('total', 'total_con_iva', 'iva_total', 'estado')

class VentaAdmin(admin.ModelAdmin):
    form = VentaAdminForm
    inlines = [DetalleVentaInline]
    list_display = ('idVenta', 'cliente', 'usuario', 'fecha_venta', 'estado', 'total_con_iva')
    readonly_fields = ('total', 'total_con_iva', 'iva_total')
    actions = ['action_confirmar_ventas', 'action_cancelar_ventas']
    autocomplete_fields = ('cliente', 'usuario')

    def action_confirmar_ventas(self, request, queryset):
        # sólo staff o superuser pueden confirmar desde admin
        if not request.user.is_staff:
            raise PermissionDenied
        for venta in queryset:
            try:
                venta.confirmar(usuario=request.user)
                self.message_user(request, f"Venta #{venta.idVenta} confirmada.")
            except Exception as e:
                self.message_user(request, f"No se pudo confirmar Venta #{venta.idVenta}: {e}", level='error')
    action_confirmar_ventas.short_description = "Confirmar ventas seleccionadas"

    def action_cancelar_ventas(self, request, queryset):
        if not request.user.is_staff:
            raise PermissionDenied
        for venta in queryset:
            try:
                venta.cancelar()
                self.message_user(request, f"Venta #{venta.idVenta} cancelada.")
            except Exception as e:
                self.message_user(request, f"No se pudo cancelar Venta #{venta.idVenta}: {e}", level='error')
    action_cancelar_ventas.short_description = "Cancelar ventas seleccionadas"

admin.site.register(Venta, VentaAdmin)
