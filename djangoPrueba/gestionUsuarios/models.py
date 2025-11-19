from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ← AGRÉGALO
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name='usuarios')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username