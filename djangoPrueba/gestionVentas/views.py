from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Venta, DetalleVenta
from gestionClientes.models import Cliente
from gestionProductos.models import Productos
from gestionUsuarios.models import Usuario

@login_required
def ventas_list(request):
    """Listado de ventas con filtros y paginación"""
    from django.core.paginator import Paginator
    from django.db.models import Sum
    
    ventas_query = Venta.objects.select_related('cliente', 'usuario').all()
    
    # Obtener parámetros de filtro
    estado_filtro = request.GET.get('estado', '')
    cliente_filtro = request.GET.get('cliente', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Aplicar filtros
    if estado_filtro:
        ventas_query = ventas_query.filter(estado=estado_filtro)
    
    if cliente_filtro:
        ventas_query = ventas_query.filter(cliente__idCliente=cliente_filtro)
    
    if fecha_desde:
        ventas_query = ventas_query.filter(fecha_venta__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas_query = ventas_query.filter(fecha_venta__date__lte=fecha_hasta)
    
    # Calcular estadísticas
    stats = {
        'pendientes': Venta.objects.filter(estado='PENDIENTE').count(),
        'confirmadas': Venta.objects.filter(estado='CONFIRMADA').count(),
        'canceladas': Venta.objects.filter(estado='CANCELADA').count(),
        'total': Venta.objects.filter(estado='CONFIRMADA').aggregate(
            total=Sum('total_con_iva')
        )['total'] or 0
    }
    
    # Paginación
    paginator = Paginator(ventas_query, 10)
    page_number = request.GET.get('page', 1)
    ventas = paginator.get_page(page_number)
    
    # Lista de clientes para el filtro
    clientes = Cliente.objects.all().order_by('nombre', 'apellido')
    
    context = {
        'ventas': ventas,
        'clientes': clientes,
        'estado_filtro': estado_filtro,
        'cliente_filtro': cliente_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'stats': stats,
    }
    
    return render(request, 'ventas_list.html', context)

@login_required
def ventas_form(request, id=None):
    """Crear o editar venta"""
    import json
    
    venta = get_object_or_404(Venta, idVenta=id) if id else None
    
    # Solo se pueden editar ventas pendientes
    if venta and venta.estado != Venta.ESTADO_PENDIENTE:
        messages.error(request, 'Solo se pueden editar ventas en estado PENDIENTE.')
        return redirect('ventas_detalle', id=venta.idVenta)
    
    if request.method == 'POST':
        try:
            # Datos de la venta
            cliente_id = request.POST.get('cliente')
            metodo_pago = request.POST.get('metodo_pago')
            observaciones = request.POST.get('observaciones', '')
            
            # Validaciones
            if not cliente_id:
                raise ValidationError('Debe seleccionar un cliente')
            
            cliente = get_object_or_404(Cliente, idCliente=cliente_id)
            
            # Obtener o crear el usuario asociado al user actual
            try:
                usuario = Usuario.objects.get(user=request.user)
            except Usuario.DoesNotExist:
                raise ValidationError('El usuario actual no tiene un perfil de Usuario asociado')
            
            # Crear o actualizar venta
            if venta:
                venta.cliente = cliente
                venta.metodo_pago = metodo_pago
                venta.observaciones = observaciones
                venta.save()
            else:
                venta = Venta.objects.create(
                    cliente=cliente,
                    usuario=usuario,
                    metodo_pago=metodo_pago,
                    observaciones=observaciones
                )
            
            # Procesar detalles
            productos_ids = request.POST.getlist('producto_id[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio_unitario[]')
            observaciones_det = request.POST.getlist('observacion_detalle[]')
            
            if not productos_ids:
                raise ValidationError('Debe agregar al menos un producto')
            
            # Eliminar detalles existentes si es edición
            if venta.idVenta:
                venta.detalles.all().delete()
            
            # Crear nuevos detalles
            for i, prod_id in enumerate(productos_ids):
                if not prod_id:
                    continue
                
                producto = get_object_or_404(Productos, idProducto=prod_id)
                cantidad = int(cantidades[i])
                precio_unitario = Decimal(precios[i])
                observacion = observaciones_det[i] if i < len(observaciones_det) else ''
                
                # Validar stock disponible
                if cantidad > producto.stock:
                    raise ValidationError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.stock}, solicitado: {cantidad}'
                    )
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    observacion=observacion
                )
            
            # Recalcular totales
            venta.calcular_total()
            
            messages.success(
                request, 
                f'Venta #{venta.idVenta} {"actualizada" if id else "creada"} exitosamente'
            )
            return redirect('ventas_detalle', id=venta.idVenta)
            
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al procesar la venta: {str(e)}')
    
    # GET request
    clientes = Cliente.objects.all().order_by('nombre', 'apellido')
    productos = Productos.objects.filter(stock__gt=0).order_by('nombre')
    
    # Preparar productos en formato JSON para JavaScript
    productos_list = []
    for prod in productos:
        productos_list.append({
            'id': prod.idProducto,
            'nombre': prod.nombre,
            'precio': str(prod.precioUnitario),
            'stock': prod.stock,
            'iva': str(prod.iva or 0)
        })
    
    detalles = []
    if venta:
        detalles = venta.detalles.select_related('producto').all()
    
    context = {
        'venta': venta,
        'clientes': clientes,
        'productos': productos,
        'productos_json': json.dumps(productos_list),
        'metodos_pago': Venta.METODO_PAGO_CHOICES,
        'detalles': detalles,
    }
    
    return render(request, 'ventas_form.html', context)

@login_required
def ventas_detalle(request, id):
    """Detalle de una venta"""
    venta = get_object_or_404(
        Venta.objects.select_related('cliente', 'usuario'),
        idVenta=id
    )
    detalles = venta.detalles.select_related('producto').all()
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    
    return render(request, 'ventas_detalle.html', context)

@login_required
def ventas_eliminar(request, id):
    """Eliminar una venta (solo si está pendiente)"""
    venta = get_object_or_404(Venta, idVenta=id)
    
    if venta.estado != Venta.ESTADO_PENDIENTE:
        messages.error(request, 'Solo se pueden eliminar ventas en estado PENDIENTE')
        return redirect('ventas_list')
    
    if request.method == 'POST':
        venta.delete()
        messages.success(request, f'Venta #{id} eliminada correctamente')
        return redirect('ventas_list')
    
    return redirect('ventas_detalle', id=id)

@login_required
def venta_confirmar(request, id):
    """Confirmar una venta y descontar stock"""
    venta = get_object_or_404(Venta, idVenta=id)
    
    if request.method == 'POST':
        try:
            venta.confirmar(usuario=request.user)
            messages.success(
                request, 
                f'Venta #{venta.idVenta} confirmada. Stock actualizado correctamente.'
            )
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al confirmar la venta: {str(e)}')
    
    return redirect('ventas_detalle', id=id)

@login_required
def venta_cancelar(request, id):
    """Cancelar una venta"""
    venta = get_object_or_404(Venta, idVenta=id)
    
    if request.method == 'POST':
        try:
            motivo = request.POST.get('motivo', '')
            venta.cancelar(motivo=motivo)
            messages.success(request, f'Venta #{venta.idVenta} cancelada correctamente')
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al cancelar la venta: {str(e)}')
    
    return redirect('ventas_detalle', id=id)

# AJAX Endpoints
@login_required
def get_producto_info(request, producto_id):
    """Obtener información de un producto para AJAX"""
    try:
        producto = Productos.objects.get(idProducto=producto_id)
        return JsonResponse({
            'success': True,
            'producto': {
                'id': producto.idProducto,
                'nombre': producto.nombre,
                'precio': str(producto.precioUnitario),
                'stock': producto.stock,
                'iva': str(producto.iva or 0),
                'codigo': producto.codigo or '',
            }
        })
    except Productos.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)

@login_required
def get_cliente_info(request, cliente_id):
    """Obtener información de un cliente para AJAX"""
    try:
        cliente = Cliente.objects.get(idCliente=cliente_id)
        return JsonResponse({
            'success': True,
            'cliente': {
                'id': cliente.idCliente,
                'nombre': cliente.nombre_completo(),
                'email': cliente.email or '',
                'telefono': cliente.telefono or '',
                'direccion': cliente.direccion or '',
            }
        })
    except Cliente.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=404)