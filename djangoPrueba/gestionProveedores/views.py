from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Proveedor
from .form import ProveedorForm


@login_required
def proveedores_list(request):
    """
    Vista para listar todos los proveedores
    """
    proveedores = Proveedor.objects.all().order_by('-activo', 'razon_social')
    
    # Búsqueda opcional
    query = request.GET.get('q')
    if query:
        proveedores = proveedores.filter(
            Q(razon_social__icontains=query) |
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(cuit__icontains=query) |
            Q(email__icontains=query)
        )
    
    context = {
        'proveedores': proveedores,
    }
    return render(request, 'proveedor_list.html', context)


@login_required
def proveedor_detalle(request, pk):
    """
    Vista para mostrar el detalle de un proveedor
    """
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    context = {
        'proveedor': proveedor,
    }
    return render(request, 'proveedor_detalle.html', context)


@login_required
def proveedor_crear(request):
    """
    Vista para crear un nuevo proveedor
    """
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(
                request, 
                f'Proveedor "{proveedor.razon_social}" creado exitosamente.'
            )
            return redirect('proveedor_detalle', pk=proveedor.idProveedor)
        else:
            messages.error(
                request, 
                'Por favor corrija los errores en el formulario.'
            )
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
        'accion': 'Crear',
    }
    return render(request, 'proveedor_form.html', context)


@login_required
def proveedor_editar(request, pk):
    """
    Vista para editar un proveedor existente
    """
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            messages.success(
                request, 
                f'Proveedor "{proveedor.razon_social}" actualizado exitosamente.'
            )
            return redirect('proveedor_detalle', pk=proveedor.idProveedor)
        else:
            messages.error(
                request, 
                'Por favor corrija los errores en el formulario.'
            )
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor,
        'accion': 'Editar',
    }
    return render(request, 'proveedor_form.html', context)


@login_required
def proveedor_confirmar_eliminar(request, pk):
    """
    Vista para confirmar la desactivación de un proveedor
    """
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        # Desactivar en lugar de eliminar
        proveedor.activo = False
        proveedor.save()
        
        messages.success(
            request, 
            f'Proveedor "{proveedor.razon_social}" desactivado correctamente.'
        )
        return redirect('proveedores_list')
    
    context = {
        'proveedor': proveedor,
    }
    return render(request, 'confirmar_eliminar.html', context)


@login_required
def proveedor_activar(request, pk):
    """
    Vista para reactivar un proveedor
    (Opcional - por si quieres reactivar proveedores desactivados)
    """
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    proveedor.activo = True
    proveedor.save()
    
    messages.success(
        request, 
        f'Proveedor "{proveedor.razon_social}" reactivado correctamente.'
    )
    return redirect('proveedor_detalle', pk=proveedor.idProveedor)