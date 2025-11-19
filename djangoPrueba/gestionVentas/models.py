from django.db import models
from gestionClientes.models import Cliente
from gestionUsuarios.models import Usuario
from gestionProductos.models import Productos

# Register your models here.
class Venta(models.Model):

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('MERCADOPAGO', 'MercadoPago'),
    ]
    
    idVenta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ventas_realizadas')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='EFECTIVO')
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.idVenta} - {self.cliente.nombre_completo()}"
    
    def calcular_total(self):
        """Calcula el total de la venta sumando todos los detalles"""
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save()
        return total

class DetalleVenta(models.Model):
    idDetalleVenta = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Productos, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=9, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"Detalle #{self.idDetalleVenta} - Venta #{self.venta.idVenta}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualizar el total de la venta
        self.venta.calcular_total()