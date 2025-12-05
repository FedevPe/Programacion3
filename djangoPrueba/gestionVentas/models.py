# gestionVentas/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from gestionClientes.models import Cliente
from gestionUsuarios.models import Usuario
from gestionProductos.models import Productos

class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('MERCADOPAGO', 'MercadoPago'),
    ]

    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_CONFIRMADA = 'CONFIRMADA'
    ESTADO_CANCELADA = 'CANCELADA'
    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]
    
    idVenta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ventas_realizadas')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='EFECTIVO')

    # Totales calculados (no editables por form normalmente)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_con_iva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    iva_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    estado = models.CharField(max_length=15, choices=ESTADOS_CHOICES, default=ESTADO_PENDIENTE)
    observaciones = models.TextField(null=True, max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.idVenta} - {self.cliente.nombre_completo()}"

    def calcular_total(self):
        detalles = self.detalles.all()
        total = sum((det.subtotal for det in detalles), Decimal('0.00'))
        total_con_iva = sum((det.subtotal_con_iva for det in detalles), Decimal('0.00'))
        iva_total = sum((det.iva_monto for det in detalles), Decimal('0.00'))

        # Guardar sin reentrar en loops infinitos
        self.total = total
        self.total_con_iva = total_con_iva
        self.iva_total = iva_total
        self.save(update_fields=['total', 'total_con_iva', 'iva_total'])
        return total

    def confirmar(self, usuario=None):
        """
        Confirmar la venta: validar stock nuevamente y descontar.
        Debe llamarse en un contexto donde el usuario tenga permisos (ver views/admin).
        """
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValidationError("Solo ventas pendientes pueden confirmarse.")

        detalles = self.detalles.select_related('producto').all()

        with transaction.atomic():
            # Re-check stock y descontar
            for det in detalles:
                prod = det.producto
                if det.cantidad > prod.stock:
                    raise ValidationError(
                        f"Stock insuficiente para el producto '{prod.nombre}'. "
                        f"Disponible: {prod.stock}, requerido: {det.cantidad}"
                    )
                # descontar
                prod.stock = prod.stock - det.cantidad
                prod.save(update_fields=['stock'])

            # cambiar estado
            self.estado = self.ESTADO_CONFIRMADA
            self.save(update_fields=['estado'])

    def cancelar(self, motivo=None):
        """
        Cancelar la venta: solo cambia estado si estaba pendiente. 
        (Si querés revertir stock para ventas ya confirmadas, habría otra lógica.)
        """
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValidationError("Solo ventas pendientes pueden cancelarse.")
        self.estado = self.ESTADO_CANCELADA
        self.save(update_fields=['estado'])

class DetalleVenta(models.Model):
    idDetalleVenta = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Productos, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    iva_porcentaje = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    iva_monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal_con_iva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    observacion = models.TextField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self):
        return f"Detalle #{self.idDetalleVenta} - Venta #{self.venta.idVenta}"

    @property
    def subtotal(self):
        if not self.cantidad or not self.precio_unitario:
            return Decimal('0.00')
        return (Decimal(self.cantidad) * Decimal(self.precio_unitario))

    @property
    def subtotal_con_iva(self):
        # property placeholder; we also persist subtotal_con_iva in DB for reporting
        base = self.subtotal
        iva = (base * (self.iva_porcentaje or Decimal('0'))) / Decimal('100')
        return base + iva

    def clean(self):
        """
        Validaciones antes de save:
        - cantidad > 0
        - no superar stock al momento de ingresar (solicitaste validar al ingresar)
        """
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        # Si la venta ya fue confirmada, no permitir cambiar detalle (opcional)
        # Validar stock: en este diseño, bloqueamos ingresar una línea si supera stock actual
        if self.cantidad > self.producto.stock:
            raise ValidationError(f"Cantidad ({self.cantidad}) supera el stock disponible ({self.producto.stock}) para el producto {self.producto.nombre}.")

    def save(self, *args, **kwargs):
        # Asignar precio y iva del producto si no se pasaron explícitamente
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precioUnitario
        self.iva_porcentaje = self.producto.iva or Decimal('0.00')

        # calcular montos
        base = self.subtotal
        self.iva_monto = (base * (self.iva_porcentaje or Decimal('0'))) / Decimal('100')
        self.subtotal_con_iva = base + self.iva_monto

        # validar antes de guardar
        self.full_clean()  # dispara clean() y demás validaciones

        super().save(*args, **kwargs)

        # actualizar totales de la venta (evitar reentradas costosas)
        try:
            self.venta.calcular_total()
        except Exception:
            # si la venta se borró o hay otro problema, no interrumpir el guardado aquí
            pass
