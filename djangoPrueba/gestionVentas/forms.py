from django import forms
from .models import Venta, DetalleVenta

# ====================
# FORMULARIO DE VENTA
# ====================
class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'metodo_pago', 'estado', 'observaciones']
        labels = {
            'cliente': 'Cliente',
            'metodo_pago': 'Método de Pago',
            'estado': 'Estado',
            'observaciones': 'Observaciones'
        }
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales'
            })
        }

# ====================
# FORMULARIO DE DETALLE DE VENTA
# ====================
class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario'
        }
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control producto-select',
                'onchange': 'actualizarPrecio(this)'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'min': '1',
                'value': '1',
                'onchange': 'calcularSubtotal(this)'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'step': '0.01',
                'readonly': 'readonly'
            })
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')
        
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        
        if producto and cantidad > producto.stock:
            raise forms.ValidationError(f'Stock insuficiente. Disponible: {producto.stock}')
        
        return cantidad