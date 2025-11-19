from django.contrib import admin
from .models import Proveedor, ProductoProveedor

# Register your models here.
# ====================
# CONFIGURACIÓN DE PROVEEDOR
# ====================
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('idProveedor', 'nombre', 'telefono', 'email')
    search_fields = ('nombre', 'email', 'telefono')
    ordering = ('nombre',)


# ====================
# CONFIGURACIÓN DE PRODUCTO-PROVEEDOR
# ====================
@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = ('producto', 'proveedor', 'precio', 'fecha_acuerdo')
    list_filter = ('proveedor', 'fecha_acuerdo')
    search_fields = ('producto__nombre', 'proveedor__nombre')
    ordering = ('-fecha_acuerdo',)
    autocomplete_fields = ['producto', 'proveedor']