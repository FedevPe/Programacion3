from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Productos, Marca, Categoria
from .forms import ProductoForm, MarcaForm, CategoriaForm
from gestionCompras.models import DetalleCompra, Compra
from gestionVentas.models import DetalleVenta, Venta




# ============================================================
# PRODUCTOS
# ============================================================
@login_required
def productos_list(request):
    # Obtener parámetros de filtro
    categoria_id = request.GET.get('categoria', '')
    marca_id = request.GET.get('marca', '')
    estado = request.GET.get('estado', '')
    codigo = request.GET.get('codigo', '')
    page = request.GET.get('page', 1)
    
    # Consulta base
    productos = Productos.objects.select_related('idMarca', 'idCategoria').all()
    
    # Aplicar filtros
    if categoria_id:
        productos = productos.filter(idCategoria_id=categoria_id)
    
    if marca_id:
        productos = productos.filter(idMarca_id=marca_id)
    
    if estado:
        productos = productos.filter(activo=(estado == 'activo'))
    
    if codigo:
        productos = productos.filter(codProducto__icontains=codigo)
    
    
    # Paginación
    paginator = Paginator(productos, 10)  # 10 productos por página
    productos_page = paginator.get_page(page)
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        productos_data = []
        for p in productos_page:
            productos_data.append({
                'idProducto': p.idProducto,
                'codProducto': p.codProducto,
                'nombre': p.nombre,
                'marca': p.idMarca.nombre,
                'categoria': p.idCategoria.descripcion,
                'precioUnitario': str(p.precioUnitario),
                'stock': p.stock,
                'activo': p.activo,
            })
        
        return JsonResponse({
            'productos': productos_data,
            'has_next': productos_page.has_next(),
            'has_previous': productos_page.has_previous(),
            'current_page': productos_page.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
        })
    
    # Obtener todas las marcas y categorías para los filtros
    marcas = Marca.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('descripcion')
    
    context = {
        'productos': productos_page,
        'marcas': marcas,
        'categorias': categorias,
        'filtros': {
            'categoria': categoria_id,
            'marca': marca_id,
            'estado': estado,
            'codigo': codigo,
        }
    }
    
    return render(request, "productos/productos_list.html", context)


@login_required
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado con éxito.")
            return redirect("productos_list")
    else:
        form = ProductoForm()

    return render(request, "productos/productos_form.html", {"form": form})


@login_required
def producto_editar(request, id):
    producto = get_object_or_404(Productos, pk=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos_list")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/productos_form.html", {"form": form})

@login_required
def producto_detalle(request, id):
    # Recupera el objeto Productos con el id proporcionado, o lanza un 404 si no existe.
    producto = get_object_or_404(Productos.objects.select_related('idMarca', 'idCategoria'), pk=id)    
    producto.precio_sin_iva = producto.precioUnitario / (1 + (producto.iva / 100))
    producto.precio_con_iva = producto.precioUnitario

    # Renderiza la plantilla de detalle, pasando el objeto producto.
    return render(request, "productos/productos_detalle.html", {"producto": producto})

@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Productos, pk=id)

    if request.method == "POST":
        # Cambiar estado a inactivo en lugar de eliminar
        producto.activo = False
        producto.save()
        
        # Si es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Producto "{producto.nombre}" desactivado correctamente.'
            })
        
        messages.success(request, f'Producto "{producto.nombre}" desactivado correctamente.')
        return redirect("productos_list")
    
    # Si es AJAX GET, devolver datos del producto
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': producto.idProducto,
            'nombre': producto.nombre,
            'codigo': producto.codProducto,
        })

    # Si es GET normal: mostrar confirmación
    return render(request, "productos/productos_confirm_delete.html", {"producto": producto})

# ============================================================
# MARCAS
# ============================================================
@login_required
def marcas_list(request):
    marcas = Marca.objects.all()
    return render(request, "marcas/marcas_list.html", {"marcas": marcas})


@login_required
def marca_crear(request):
    if request.method == "POST":
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca creada con éxito.")
            return redirect("marcas_list")
    else:
        form = MarcaForm()

    return render(request, "marcas/marcas_form.html", {"form": form})

def marca_editar(request, id):
    marca = get_object_or_404(Marca, pk=id)

    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca actualizada correctamente.")
            return redirect("marcas_list")
    else:
        form = MarcaForm(instance=marca)

    return render(request, "marcas/marcas_form.html", {"form": form, "accion": "Editar"})


@login_required
def marca_eliminar(request, id):
    marca = get_object_or_404(Marca, pk=id)

    if request.method == "POST":
        marca.delete()
        messages.success(request, f"Marca '{marca.nombre}' eliminada.")
        return redirect("marcas_list")

    return render(request, "marcas/marcas_confirm_delete.html", {"marca": marca})


# ============================================================
# CATEGORÍAS
# ============================================================
@login_required
def categorias_list(request):
    categorias = Categoria.objects.all()
    return render(request, "categorias/categorias_list.html", {"categorias": categorias})


@login_required
def categoria_crear(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada.")
            return redirect("categorias_list")
    else:
        form = CategoriaForm()

    return render(request, "categorias/categorias_form.html", {"form": form})

@login_required
def categoria_editar(request, id):
    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect("categorias_list")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "categorias/categorias_form.html", {"form": form, "accion": "Editar"})

@login_required
def categoria_eliminar(request, id):
    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == "POST":
        nombre = categoria.descripcion
        categoria.delete()
        messages.success(request, f"Categoría '{nombre}' eliminada.")
        return redirect("categorias_list")

    return render(request, "categorias/categorias_confirm_delete.html", {"categoria": categoria})

@login_required
def marca_crear_ajax(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")

        if not nombre:
            return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

        marca = Marca.objects.create(nombre=nombre)

        return JsonResponse({
            "id": marca.idMarca,
            "nombre": marca.nombre
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def categoria_crear_ajax(request):
    if request.method == "POST":
        descripcion = request.POST.get("descripcion")

        if not descripcion:
            return JsonResponse({"error": "La descripción es obligatoria"}, status=400)

        categoria = Categoria.objects.create(descripcion=descripcion)

        return JsonResponse({
            "id": categoria.idCategoria,
            "descripcion": categoria.descripcion
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)

@login_required
def transferencias_stock(request):
    """
    Vista principal para mostrar las transferencias de stock (entradas y salidas)
    """
    # Obtener todos los productos para el filtro
    productos = Productos.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'productos': productos,
    }
    
    return render(request, "transferencias/transferencias_stock.html", context)


@login_required
def transferencias_stock_ajax(request):
    """
    Vista AJAX para obtener las transferencias de stock con filtros y paginación
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Petición no válida'}, status=400)
    
    # Obtener parámetros de filtro
    producto_id = request.GET.get('producto', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    tipo_movimiento = request.GET.get('tipo', '')  # 'entrada', 'salida', o vacío (todos)
    page = int(request.GET.get('page', 1))
    per_page = 15
    
    # Validar y parsear fechas
    fecha_desde_obj = None
    fecha_hasta_obj = None
    
    if fecha_desde:
        try:
            fecha_desde_obj = parse_date(fecha_desde)
            if not fecha_desde_obj:
                return JsonResponse({'error': 'Fecha desde inválida'}, status=400)
        except:
            return JsonResponse({'error': 'Formato de fecha desde incorrecto'}, status=400)
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = parse_date(fecha_hasta)
            if not fecha_hasta_obj:
                return JsonResponse({'error': 'Fecha hasta inválida'}, status=400)
            # Agregar 23:59:59 para incluir todo el día
            fecha_hasta_obj = datetime.combine(fecha_hasta_obj, datetime.max.time())
        except:
            return JsonResponse({'error': 'Formato de fecha hasta incorrecto'}, status=400)
    
    # Validar que fecha_desde sea menor que fecha_hasta
    if fecha_desde_obj and fecha_hasta_obj and fecha_desde_obj > fecha_hasta_obj.date():
        return JsonResponse({'error': 'La fecha desde no puede ser mayor que la fecha hasta'}, status=400)
    
    # Lista para almacenar todos los movimientos
    movimientos = []
    
    # ENTRADAS (Compras confirmadas)
    if tipo_movimiento in ('', 'entrada'):
        compras_query = DetalleCompra.objects.select_related(
            'compra', 'compra__proveedor', 'producto', 'producto__idMarca', 'producto__idCategoria'
        ).filter(
            compra__estado='CONFIRMADA'
        )
        
        # Aplicar filtros
        if producto_id:
            compras_query = compras_query.filter(producto_id=producto_id)
        
        if fecha_desde_obj:
            compras_query = compras_query.filter(compra__fecha_compra__gte=fecha_desde_obj)
        
        if fecha_hasta_obj:
            compras_query = compras_query.filter(compra__fecha_compra__lte=fecha_hasta_obj)
        
        # Convertir a lista de diccionarios
        for detalle in compras_query:
            movimientos.append({
                'tipo': 'entrada',
                'fecha': detalle.compra.fecha_compra,
                'producto_id': detalle.producto.idProducto,
                'producto_nombre': detalle.producto.nombre,
                'producto_codigo': detalle.producto.codProducto,
                'marca': detalle.producto.idMarca.nombre,
                'categoria': detalle.producto.idCategoria.descripcion,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal),
                'referencia_tipo': 'Compra',
                'referencia_id': detalle.compra.idCompra,
                'referencia_nombre': detalle.compra.proveedor.razon_social,
                'observacion': detalle.observacion or '',
            })
    
    # SALIDAS (Ventas confirmadas)
    if tipo_movimiento in ('', 'salida'):
        ventas_query = DetalleVenta.objects.select_related(
            'venta', 'venta__cliente', 'producto', 'producto__idMarca', 'producto__idCategoria'
        ).filter(
            venta__estado='CONFIRMADA'
        )
        
        # Aplicar filtros
        if producto_id:
            ventas_query = ventas_query.filter(producto_id=producto_id)
        
        if fecha_desde_obj:
            ventas_query = ventas_query.filter(venta__fecha_venta__gte=fecha_desde_obj)
        
        if fecha_hasta_obj:
            ventas_query = ventas_query.filter(venta__fecha_venta__lte=fecha_hasta_obj)
        
        # Convertir a lista de diccionarios
        for detalle in ventas_query:
            movimientos.append({
                'tipo': 'salida',
                'fecha': detalle.venta.fecha_venta,
                'producto_id': detalle.producto.idProducto,
                'producto_nombre': detalle.producto.nombre,
                'producto_codigo': detalle.producto.codProducto,
                'marca': detalle.producto.idMarca.nombre,
                'categoria': detalle.producto.idCategoria.descripcion,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal),
                'referencia_tipo': 'Venta',
                'referencia_id': detalle.venta.idVenta,
                'referencia_nombre': detalle.venta.cliente.nombre_completo(),
                'observacion': detalle.observacion or '',
            })
    
    # Ordenar por fecha descendente
    movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    
    # Calcular estadísticas
    total_registros = len(movimientos)
    total_entradas = sum(1 for m in movimientos if m['tipo'] == 'entrada')
    total_salidas = sum(1 for m in movimientos if m['tipo'] == 'salida')
    
    # Paginación manual
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    movimientos_page = movimientos[start_idx:end_idx]
    
    total_pages = (total_registros + per_page - 1) // per_page
    
    # Formatear fechas para JSON
    for mov in movimientos_page:
        mov['fecha'] = mov['fecha'].strftime('%d/%m/%Y %H:%M')
    
    return JsonResponse({
        'success': True,
        'movimientos': movimientos_page,
        'estadisticas': {
            'total_registros': total_registros,
            'total_entradas': total_entradas,
            'total_salidas': total_salidas,
        },
        'paginacion': {
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'total_count': total_registros,
        }
    })