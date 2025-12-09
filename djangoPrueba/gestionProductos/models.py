from django.db import models

# Create your models here.

class Marca(models.Model):
    idMarca = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=25)

    class Meta:
        verbose_name='Marca'
        verbose_name_plural='Marcas'

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name='Categoría'
        verbose_name_plural='Categorías'

    def __str__(self):
        return self.descripcion

class Productos(models.Model):
    IVA_21 = 21.00
    IVA_105 = 10.50
    IVA_27 = 27.00
    IVA_0 = 0.00

    OPCIONES_IVA = [
        (IVA_21, "21%"),
        (IVA_105, "10.5%"),
        (IVA_27, "27%"),
        (IVA_0, "Exento (0%)"),    
    ]


    idProducto = models.AutoField(primary_key=True)
    codProducto = models.CharField(max_length=10)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    imgUrl = models.CharField(max_length=500, default='')
    precioUnitario = models.DecimalField(max_digits=18, decimal_places=2)
    idMarca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING, related_name='Marca')
    idCategoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING, related_name='Categoria')
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    # NUEVO CAMPO
    iva = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        choices=OPCIONES_IVA,
        default=IVA_21
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre



