from django.contrib import admin
from .models import Venta
from .models import DetalleVenta

# ====================
# INLINE PARA DETALLE DE VENTA
# ====================
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ['producto']


# ====================
# CONFIGURACIÓN DE VENTA
# ====================
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('idVenta', 'cliente', 'usuario', 'fecha_venta', 'total', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_venta')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'usuario__username')
    ordering = ('-fecha_venta',)
    inlines = [DetalleVentaInline]
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('cliente', 'usuario')
        }),
        ('Detalles de Pago', {
            'fields': ('metodo_pago', 'total')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_venta',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_venta', 'total')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva venta
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

# ====================
# CONFIGURACIÓN DE DETALLE DE VENTA
# ====================
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('idDetalleVenta', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha_venta',)
    search_fields = ('venta__idVenta', 'producto__nombre')
    ordering = ('-venta__fecha_venta',)
    readonly_fields = ('subtotal',)
    
    fieldsets = (
        ('Venta', {
            'fields': ('venta',)
        }),
        ('Producto', {
            'fields': ('producto', 'cantidad', 'precio_unitario')
        }),
        ('Total', {
            'fields': ('subtotal',)
        }),
    )