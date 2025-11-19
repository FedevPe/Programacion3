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
    idProducto = models.AutoField(primary_key=True)
    codProducto = models.CharField(max_length = 5)
    nombre = models.CharField(max_length = 150)
    descripcion = models.TextField()
    imgUrl = models.CharField(max_length=500, default='')
    precioUnitario = models.DecimalField(max_digits=9, decimal_places=2)
    idMarca= models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='Marca')
    idCategoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='Categoria')
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name='Producto'
        verbose_name_plural='Productos'

    def __str__(self):
        return self.nombre



