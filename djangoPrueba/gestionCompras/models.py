from django.db import models
from decimal import Decimal
from gestionProveedores.models import Proveedor
from gestionUsuarios.models import Usuario
from gestionProductos.models import Productos


class Compra(models.Model):

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('MERCADOPAGO', 'MercadoPago'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ]

    idCompra = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')

    fecha_compra = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='EFECTIVO')

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_con_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observaciones = models.TextField(null=True, blank=True, max_length=200)

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"Compra #{self.idCompra} - {self.proveedor.nombre}"

    # Cálculo de totales
    def calcular_totales(self):
        detalles = self.detalles.all()
        self.total = sum(det.subtotal for det in detalles)
        self.total_con_iva = sum(det.subtotal_con_iva for det in detalles)
        self.iva_total = sum(det.iva_monto for det in detalles)
        self.save(update_fields=['total', 'total_con_iva', 'iva_total'])

    # Manejo del stock según estado
    def save(self, *args, **kwargs):
        if self.pk:
            old = Compra.objects.get(pk=self.pk)

            # PENDIENTE → CONFIRMADA = sumar stock
            if old.estado == "PENDIENTE" and self.estado == "CONFIRMADA":
                for det in self.detalles.all():
                    det.producto.stock += det.cantidad
                    det.producto.save()

            # CONFIRMADA → CANCELADA = restar stock
            if old.estado == "CONFIRMADA" and self.estado == "CANCELADA":
                for det in self.detalles.all():
                    det.producto.stock -= det.cantidad
                    det.producto.save()

        super().save(*args, **kwargs)


class DetalleCompra(models.Model):

    idDetalleCompra = models.AutoField(primary_key=True)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Productos, on_delete=models.PROTECT, related_name='detalles_compra')

    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=9, decimal_places=2)

    iva_porcentaje = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    iva_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_con_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observacion = models.TextField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Detalle de compra'
        verbose_name_plural = 'Detalles de compra'

    def __str__(self):
        return f"Detalle #{self.idDetalleCompra} - Compra #{self.compra.idCompra}"

    @property
    def subtotal(self):
        if not self.cantidad or not self.precio_unitario:
            return Decimal('0')
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        self.iva_porcentaje = self.producto.iva or 0
        base = self.subtotal
        self.iva_monto = (base * self.iva_porcentaje) / 100
        self.subtotal_con_iva = base + self.iva_monto

        super().save(*args, **kwargs)

        # actualizar totales del encabezado
        self.compra.calcular_totales()
