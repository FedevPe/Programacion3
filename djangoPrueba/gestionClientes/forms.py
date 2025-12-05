from .models import Cliente
from django import forms
import re

# ====================
# FORMULARIO DE CLIENTES
# ====================
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'dni', 'email', 'telefono', 'direccion']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'email': 'Email',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +54 261 1234567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            })
        }
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')

        # Si está vacío, dejar que la validación 'required' lo gestione (o lanzar error si querés)
        if dni in (None, ''):
            return dni

        # Normalizar: asegurar string sin espacios
        dni_str = str(dni).strip()

        # Formato: solo números
        if not dni_str.isdigit():
            raise forms.ValidationError("El DNI solo puede contener números.")

        # Longitud: máximo 8 caracteres
        if len(dni_str) > 8:
            raise forms.ValidationError("El DNI no puede tener más de 8 dígitos.")

        # Unicidad: buscar otros clientes con el mismo DNI
        qs = Cliente.objects.filter(dni=dni_str)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe un cliente con este DNI.")

        # Devolver el valor en el tipo esperado por el modelo.
        # Si en el model el campo es CharField devolvemos string:
        return dni_str

    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")

        if len(nombre) > 100:
            raise forms.ValidationError("El nombre no puede superar los 100 caracteres.")

        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")

        if len(apellido) > 100:
            raise forms.ValidationError("El apellido no puede superar los 100 caracteres.")

        return apellido
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not re.match(r'^\d{7,15}$', telefono):
            raise forms.ValidationError("El teléfono debe contener entre 7 y 15 dígitos.")

        return telefono