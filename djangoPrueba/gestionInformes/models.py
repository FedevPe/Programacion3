# from django.db import models
# from gestionUsuarios.models import Usuario

# # Modelo opcional para guardar reportes personalizados o favoritos
# class ReporteGuardado(models.Model):
#     TIPO_REPORTE_CHOICES = [
#         ('VENTAS_MENSUALES', 'Ventas Mensuales'),
#         ('PRODUCTOS_MAS_VENDIDOS', 'Productos Más Vendidos'),
#         ('TOP_PROVEEDORES', 'Top Proveedores'),
#         ('TOP_CLIENTES', 'Top Clientes'),
#         ('FLUJO_CAJA', 'Flujo de Caja'),
#     ]
    
#     idReporte = models.AutoField(primary_key=True)
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes_guardados')
#     tipo_reporte = models.CharField(max_length=30, choices=TIPO_REPORTE_CHOICES)
#     nombre = models.CharField(max_length=100)
#     fecha_desde = models.DateField(null=True, blank=True)
#     fecha_hasta = models.DateField(null=True, blank=True)
#     fecha_creacion = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name = 'Reporte Guardado'
#         verbose_name_plural = 'Reportes Guardados'
#         ordering = ['-fecha_creacion']
    
#     def __str__(self):
#         return f"{self.nombre} - {self.usuario.username}"