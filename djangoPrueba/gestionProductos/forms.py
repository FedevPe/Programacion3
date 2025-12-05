from django import forms
from .models import Productos, Marca, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = [
            'codProducto', 'nombre', 'descripcion', 'imgUrl',
            'precioUnitario', 'idMarca', 'idCategoria', 'stock', 'activo', 'iva'
        ]
        labels = {
            'codProducto': 'Código de Producto',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'imgUrl': 'URL de Imagen',
            'precioUnitario': 'Precio Unitario',
            'idMarca': 'Marca',
            'idCategoria': 'Categoría',
            'stock': 'Stock',
            'activo': 'Activo',
            'iva' : 'IVA'
        }
        widgets = {
            'codProducto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: P0001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del producto'
            }),
            'imgUrl': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/imagen.jpg'
            }),
            'precioUnitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'idMarca': forms.Select(attrs={
                'class': 'form-control'
            }),
            'idCategoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'iva': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    # -------------------------
    # VALIDACIONES PERSONALIZADAS
    # -------------------------
    def clean_codProducto(self):
        cod = self.cleaned_data.get('codProducto')
        if len(cod) >= 10:
            raise forms.ValidationError('El código no puede tener más de 10 caracteres')
        return cod.upper()

    def clean_precioUnitario(self):
        precio = self.cleaned_data.get('precioUnitario')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return precio
    
    def clean_iva(self):
        ivaProducto = self.cleaned_data.get('iva')
        if ivaProducto is None or ivaProducto == "":
            raise forms.ValidationError('Debe establecer la categoría de IVA para el producto')
        return float(ivaProducto)

    # -------------------------
    # CONFIGURAR VISIBILIDAD DE "activo"
    # -------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si NO tiene PK → es creación → ocultar campo "activo"
        if not self.instance.pk:
            self.fields['activo'].widget = forms.HiddenInput()
            self.fields['activo'].initial = True

    # Refuerzo opcional para que siempre se guarde activo=True en creación
    def save(self, commit=True):
        producto = super().save(commit=False)

        if not self.instance.pk:
            producto.activo = True  # siempre activo al crear

        if commit:
            producto.save()
        return producto

# ====================
# FORMULARIO DE BÚSQUEDA
# ====================
class BusquedaProductoForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, código o descripción...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    marca = forms.ModelChoiceField(
        queryset=Marca.objects.all(),
        required=False,
        empty_label='Todas las marcas',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

# ====================
# FORMULARIO DE MARCA
# ====================
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la marca'
            })
        }

# ====================
# FORMULARIO DE CATEGORÍA
# ====================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['descripcion']
        labels = {
            'descripcion': 'Descripción'
        }
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la categoría'
            })
        }