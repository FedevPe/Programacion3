from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
import json

from .models import Compra, DetalleCompra
from gestionProveedores.models import Proveedor
from gestionProductos.models import Productos
from gestionProveedores.models import ProductoProveedor  # tabla intermedia

@login_required
def compras_list(request):

    stats = {
        'pendientes': Compra.objects.filter(estado='PENDIENTE').count(),
        'confirmadas': Compra.objects.filter(estado='CONFIRMADA').count(),
        'canceladas': Compra.objects.filter(estado='CANCELADA').count(),
        'total': Compra.objects.filter(estado='CONFIRMADA').aggregate(Sum('total_con_iva'))['total_con_iva__sum'] or 0
    }

    """Lista todas las compras"""
    compras = Compra.objects.select_related('proveedor').all()
    
    context = {
        'compras': compras,
        'stats' : stats
    }
    return render(request, 'compras/compras_list.html', context)


@login_required
def compra_crear(request):
    """Crea una nueva compra"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                proveedor_id = request.POST.get('proveedor')
                metodo_pago = request.POST.get('metodo_pago')
                observaciones = request.POST.get('observaciones', '')
                estado = request.POST.get('estado', 'PENDIENTE')
                
                # Validar proveedor
                proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
                # Crear la compra
                compra = Compra.objects.create(
                    proveedor=proveedor,
                    metodo_pago=metodo_pago,
                    observaciones=observaciones,
                    estado=estado
                )
                
                # Procesar los productos
                productos_agregados = 0
                
                # Iterar sobre los datos POST para encontrar productos
                for key in request.POST.keys():
                    if key.startswith('producto_'):
                        # Extraer el ID del contador
                        contador = key.split('_')[1]
                        
                        idProducto = request.POST.get(f'producto_{contador}')
                        cantidad = request.POST.get(f'cantidad_{contador}')
                        precio = request.POST.get(f'precio_{contador}')
                        observacion = request.POST.get(f'observacion_{contador}', '')
                        

                        if idProducto and cantidad and precio:
                            producto = get_object_or_404(Productos, pk=idProducto)
                            # Crear el detalle
                            DetalleCompra.objects.create(
                                compra=compra,
                                producto=producto,
                                cantidad=int(cantidad),
                                precio_unitario=Decimal(precio),
                                observacion=observacion
                            )
                            productos_agregados += 1
                
                # Validar que se agregó al menos un producto
                if productos_agregados == 0:
                    raise ValueError("Debe agregar al menos un producto a la compra")
                
                # Recalcular totales
                compra.calcular_totales()
                
                # Mensaje de éxito
                if estado == 'CONFIRMADA':
                    messages.success(request, f'¡Compra #{compra.idCompra} confirmada exitosamente!')
                else:
                    messages.success(request, f'¡Compra #{compra.idCompra} guardada!')
                
                return redirect('compras_list')
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al crear la orden de compra: {str(e)}')
    
    # GET - Mostrar formulario
    proveedores = Proveedor.objects.filter(activo=True).order_by('razon_social')
    productos = Productos.objects.filter(activo=True).select_related('idMarca', 'idCategoria').order_by('nombre')
    
    # Convertir productos a JSON para usar en JavaScript
    productos_json = json.dumps([
        {
            'id': p.idProducto,
            'nombre': f"{p.nombre} - {p.idMarca.nombre if p.idMarca else 'Sin marca'}",
            'iva': float(p.iva) if p.iva else 0
        }
        for p in productos
    ])
    
    context = {
        'proveedores': proveedores,
        'productos': productos,
        'productos_json': productos_json,
    }
    
    return render(request, 'compras/compras_form.html', context)


@login_required
def compra_detalle(request, pk):
    """Ver detalle de una compra"""
    compra = get_object_or_404(
        Compra.objects.select_related('proveedor')
        .prefetch_related('detalles__producto'),
        pk=pk
    )
    
    context = {
        'compra': compra,
    }
    return render(request, 'compras/compra_detalle.html', context)

@login_required
def compra_cambiar_estado(request, pk):
    """Cambiar el estado de una compra"""
    
    if request.method == 'POST':
        compra = get_object_or_404(Compra, pk=pk)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(Compra.ESTADO_CHOICES):
            compra.estado = nuevo_estado
            compra.save()
            
            messages.success(request, f'Estado de la compra actualizado a {compra.get_estado_display()}')
        else:
            messages.error(request, 'Estado no válido')
    
    return redirect('compra_detalle', pk=pk)


@login_required
def compra_eliminar(request, pk):
    """Cambiar estado a CANCELADA en lugar de eliminar físicamente."""
    
    if request.method == 'POST':
        compra = get_object_or_404(Compra, pk=pk)

        if compra.estado == 'PENDIENTE':
            compra.estado = 'CANCELADA'
            compra.save()
            messages.success(request, 'La compra fue cancelada correctamente.')
        else:
            messages.error(request, 'Solo se pueden cancelar compras en estado PENDIENTE.')

    return redirect('compras_list')

@login_required
def obtener_productos_por_proveedor(request, proveedor_id):
    productos_rel = ProductoProveedor.objects.filter(proveedor_id=proveedor_id).select_related("producto")

    productos = [
        {
            "id": rel.producto.idProducto,
            "nombre": rel.producto.nombre,
            "iva": rel.producto.iva,
        }
        for rel in productos_rel
    ]

    return JsonResponse({"productos": productos})