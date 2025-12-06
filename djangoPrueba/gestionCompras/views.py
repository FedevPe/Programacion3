from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import Compra, DetalleCompra
from gestionProveedores.models import Proveedor
from gestionProductos.models import Productos
from gestionProveedores.models import ProductoProveedor

@login_required
def compras_list(request):
    # Obtener todas las compras inicialmente
    compras = Compra.objects.select_related('proveedor').all().order_by('-fecha_compra')
    
    # Obtener proveedores para los filtros
    proveedores = Proveedor.objects.filter(activo=True).order_by('razon_social')
    
    # Aplicar filtros si existen
    estado_filtro = request.GET.get('estado', '')
    proveedor_filtro = request.GET.get('proveedor', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Filtrar por estado
    if estado_filtro:
        compras = compras.filter(estado=estado_filtro)
    
    # Filtrar por proveedor
    if proveedor_filtro:
        compras = compras.filter(proveedor_id=proveedor_filtro)
    
    # Filtrar por fechas
    if fecha_desde and fecha_hasta:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            
            # Validar que fecha_hasta >= fecha_desde
            if fecha_hasta_obj < fecha_desde_obj:
                messages.error(request, 'La fecha hasta no puede ser anterior a la fecha desde.')
                fecha_hasta = fecha_desde
                fecha_hasta_obj = fecha_desde_obj
            
            # Si las fechas son iguales, ajustar fecha_hasta a las 23:59:59
            if fecha_desde_obj == fecha_hasta_obj:
                # Crear datetime con hora 00:00:00 para fecha_desde
                fecha_desde_dt = datetime.combine(fecha_desde_obj, datetime.min.time())
                # Crear datetime con hora 23:59:59 para fecha_hasta
                fecha_hasta_dt = datetime.combine(fecha_hasta_obj, datetime.max.time())
                
                compras = compras.filter(
                    fecha_compra__gte=fecha_desde_dt,
                    fecha_compra__lte=fecha_hasta_dt
                )
            else:
                # Si son fechas diferentes, filtrar normalmente
                compras = compras.filter(
                    fecha_compra__date__gte=fecha_desde_obj,
                    fecha_compra__date__lte=fecha_hasta_obj
                )
                
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
    elif fecha_desde:
        # Solo fecha_desde, usar todo el día
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            fecha_desde_dt = datetime.combine(fecha_desde_obj, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_desde_obj, datetime.max.time())
            
            compras = compras.filter(
                fecha_compra__gte=fecha_desde_dt,
                fecha_compra__lte=fecha_hasta_dt
            )
            fecha_hasta = fecha_desde
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
    elif fecha_hasta:
        # Solo fecha_hasta, usar todo el día
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            fecha_desde_dt = datetime.combine(fecha_hasta_obj, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta_obj, datetime.max.time())
            
            compras = compras.filter(
                fecha_compra__gte=fecha_desde_dt,
                fecha_compra__lte=fecha_hasta_dt
            )
            fecha_desde = fecha_hasta
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
    
    # Calcular estadísticas basadas en los filtros aplicados
    stats = {
        'pendientes': compras.filter(estado='PENDIENTE').count(),
        'confirmadas': compras.filter(estado='CONFIRMADA').count(),
        'canceladas': compras.filter(estado='CANCELADA').count(),
        'total': compras.filter(estado='CONFIRMADA').aggregate(Sum('total_con_iva'))['total_con_iva__sum'] or 0
    }
    
    # Configurar paginación
    paginator = Paginator(compras, 10)  # 10 compras por página
    page = request.GET.get('page')
    
    try:
        compras_paginadas = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        compras_paginadas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        compras_paginadas = paginator.page(paginator.num_pages)
    
    context = {
        'compras': compras_paginadas,
        'stats': stats,
        'proveedores': proveedores,
        'estado_filtro': estado_filtro,
        'proveedor_filtro': proveedor_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'compras_list.html', context)


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
    
    return render(request, 'compras_form.html', context)


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
    return render(request, 'compra_detalle.html', context)

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