from .models import Cliente
from django import forms

# ====================
# FORMULARIO DE CLIENTES
# ====================
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'dni', 'email', 'telefono', 'activo']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'email': 'Email',
            'telefono': 'Teléfono',
            'activo': 'Activo'
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
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        # Verificar si ya existe otro cliente con ese DNI
        if self.instance.pk:  # Si estamos editando
            if Cliente.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un cliente con este DNI')
        else:  # Si estamos creando
            if Cliente.objects.filter(dni=dni).exists():
                raise forms.ValidationError('Ya existe un cliente con este DNI')
        return dni