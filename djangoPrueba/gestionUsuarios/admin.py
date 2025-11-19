from django.contrib import admin
from .models import Usuario, Rol

# Register your models here.
# ====================
# CONFIGURACIÓN DE USUARIO
# ====================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'activo', 'fecha_registro')
    list_filter = ('rol', 'activo')
    search_fields = ('user__username', 'user__email')
    ordering = ('-fecha_registro',)

    readonly_fields = ('fecha_registro',)

    fieldsets = (
        ('Usuario asociado', {
            'fields': ('user',)
        }),
        ('Rol y Estado', {
            'fields': ('rol', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
# ====================
# CONFIGURACIÓN DE ROL
# ====================
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'cantidad_usuarios')
    search_fields = ('nombre', 'descripcion')
    
    def cantidad_usuarios(self, obj):
        return obj.usuarios.count()
    cantidad_usuarios.short_description = 'Usuarios'