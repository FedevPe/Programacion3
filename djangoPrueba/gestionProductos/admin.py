from django.contrib import admin
from .models import Marca, Categoria, Productos

# ====================
# CONFIGURACIÓN DE MARCA
# ====================
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('idMarca', 'nombre', 'cantidad_productos')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    
    def cantidad_productos(self, obj):
        return obj.Marca.count()
    cantidad_productos.short_description = 'Productos'


# ====================
# CONFIGURACIÓN DE CATEGORÍA
# ====================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('idCategoria', 'descripcion', 'cantidad_productos')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)
    
    def cantidad_productos(self, obj):
        return obj.Categoria.count()
    cantidad_productos.short_description = 'Productos'


# ====================
# CONFIGURACIÓN DE PRODUCTOS
# ====================
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('codProducto', 'nombre', 'idMarca', 'idCategoria', 'precioUnitario', 'stock', 'activo')
    list_filter = ('activo', 'idMarca', 'idCategoria', 'fecha_creacion')
    search_fields = ('codProducto', 'nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
    list_editable = ('stock', 'activo')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codProducto', 'nombre', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('idMarca', 'idCategoria')
        }),
        ('Precios e Inventario', {
            'fields': ('precioUnitario', 'stock', 'activo')
        }),
        ('Imagen', {
            'fields': ('imgUrl',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

# ====================
# PERSONALIZACIÓN DEL ADMIN SITE
# ====================
admin.site.site_header = "Sistema de Gestión - Administración"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Bienvenido al Panel de Control"