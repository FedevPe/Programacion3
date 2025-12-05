from django.db import models
from gestionProductos.models import Productos

# Create your models here.
class Proveedor(models.Model):
    idProveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    razon_social = models.CharField(max_length=100)
    cuit = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name='Proveedor'
        verbose_name_plural='Proveedores'
    
    def __str__(self):
        return self.razon_social
    
class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'proveedor')
        verbose_name = 'Producto-Proveedor'
        verbose_name_plural = 'Productos-Proveedores'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.nombre}"