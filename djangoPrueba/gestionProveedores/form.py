from django import forms
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    """
    Formulario para crear y editar proveedores
    """
    
    class Meta:
        model = Proveedor
        fields = [
            'nombre',
            'apellido',
            'razon_social',
            'cuit',
            'telefono',
            'email',
        ]
        
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'razon_social': 'Razón Social',
            'cuit': 'CUIT',
            'telefono': 'Teléfono',
            'email': 'Email',
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre',
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido',
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la razón social',
            }),
            'cuit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX-XXXXXXXX-XX',
                'maxlength': '13',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com',
            }),
        }
        
        help_texts = {
            'cuit': 'Formato: XX-XXXXXXXX-XX',
            'telefono': 'Incluya código de área',
            'email': 'Email de contacto del proveedor',
        }
    
    def clean_cuit(self):
        """
        Validación personalizada para el CUIT
        """
        cuit = self.cleaned_data.get('cuit')
        
        # Eliminar espacios y guiones para validar
        cuit_limpio = cuit.replace('-', '').replace(' ', '')
        
        # Verificar que tenga 11 dígitos
        if not cuit_limpio.isdigit() or len(cuit_limpio) != 11:
            raise forms.ValidationError(
                'El CUIT debe contener exactamente 13 dígitos numéricos.'
            )
        
        # Verificar que no exista otro proveedor con el mismo CUIT
        # (excluyendo el actual si es una edición)
        instance = self.instance
        if Proveedor.objects.filter(cuit=cuit).exclude(pk=instance.pk).exists():
            raise forms.ValidationError(
                'Ya existe un proveedor registrado con este CUIT.'
            )
        
        return cuit
    
    def clean_email(self):
        """
        Validación personalizada para el email
        """
        email = self.cleaned_data.get('email')
        
        if email:
            # Verificar que no exista otro proveedor con el mismo email
            # (excluyendo el actual si es una edición)
            instance = self.instance
            if Proveedor.objects.filter(email=email).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(
                    'Ya existe un proveedor registrado con este email.'
                )
        
        return email
    
    def clean_razon_social(self):
        """
        Validación personalizada para la razón social
        """
        razon_social = self.cleaned_data.get('razon_social')
        
        if razon_social:
            # Convertir a mayúsculas la primera letra de cada palabra
            razon_social = razon_social.title()
        
        return razon_social