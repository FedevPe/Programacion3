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
    list_display = ('producto', 'proveedor')
    list_filter = ('proveedor',)
    search_fields = ('producto__nombre', 'proveedor__razon_social')
    autocomplete_fields = ['producto', 'proveedor']