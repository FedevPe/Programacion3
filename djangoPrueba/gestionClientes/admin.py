from django.contrib import admin
from .models import Cliente

# Register your models here.
# ====================
# CONFIGURACIÓN DE CLIENTE
# ====================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre_completo', 'email', 'telefono', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'dni', 'email', 'telefono')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'dni')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'telefono', 'direccion')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_registro')
        }),
    )
    
    readonly_fields = ('fecha_registro',)