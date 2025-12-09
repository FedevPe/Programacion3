from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from .utils import (
    calcular_flujo_caja,
    obtener_ventas_mensuales,
    obtener_compras_mensuales,
    obtener_productos_mas_vendidos,
    obtener_top_proveedores,
    obtener_top_clientes,
    obtener_estadisticas_generales
)

@login_required
def dashboard_informes(request):
    """
    Vista principal del dashboard de informes.
    Muestra todos los reportes en una sola página.
    """
    # Obtener parámetros de fecha (opcional)
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Convertir strings a fechas si existen
    if fecha_desde:
        try:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        except ValueError:
            fecha_desde = None
    
    if fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        except ValueError:
            fecha_hasta = None
    
    # Si no hay fechas, usar último mes por defecto
    if not fecha_desde and not fecha_hasta:
        fecha_hasta = datetime.now().date()
        fecha_desde = fecha_hasta - timedelta(days=30)
    
    # Obtener todos los datos
    flujo_caja = calcular_flujo_caja(fecha_desde, fecha_hasta)
    ventas_mensuales = obtener_ventas_mensuales(datetime.now().year)
    compras_mensuales = obtener_compras_mensuales(datetime.now().year)  # NUEVA LÍNEA
    productos_top = obtener_productos_mas_vendidos(5, fecha_desde, fecha_hasta)
    proveedores_top = obtener_top_proveedores(5, fecha_desde, fecha_hasta)
    clientes_top = obtener_top_clientes(5, fecha_desde, fecha_hasta)
    estadisticas = obtener_estadisticas_generales(fecha_desde, fecha_hasta)
    
    context = {
        'flujo_caja': flujo_caja,
        'ventas_mensuales': ventas_mensuales,
        'compras_mensuales': compras_mensuales,  # NUEVA LÍNEA
        'productos_top': productos_top,
        'proveedores_top': proveedores_top,
        'clientes_top': clientes_top,
        'estadisticas': estadisticas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def api_flujo_caja(request):
    """
    API endpoint para obtener flujo de caja (para gráficos dinámicos).
    """
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    datos = calcular_flujo_caja(fecha_desde, fecha_hasta)
    
    return JsonResponse({
        'success': True,
        'data': {
            'ingresos': str(datos['ingresos']),
            'egresos': str(datos['egresos']),
            'balance': str(datos['balance'])
        }
    })


@login_required
def api_ventas_mensuales(request):
    """
    API endpoint para obtener ventas mensuales.
    """
    anio = request.GET.get('anio', datetime.now().year)
    try:
        anio = int(anio)
    except ValueError:
        anio = datetime.now().year
    
    datos = obtener_ventas_mensuales(anio)
    
    return JsonResponse({
        'success': True,
        'data': datos
    })


@login_required
def api_productos_top(request):
    """
    API endpoint para productos más vendidos.
    """
    limite = int(request.GET.get('limite', 5))
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    datos = obtener_productos_mas_vendidos(limite, fecha_desde, fecha_hasta)
    
    return JsonResponse({
        'success': True,
        'data': datos
    })


@login_required
def api_proveedores_top(request):
    """
    API endpoint para top proveedores.
    """
    limite = int(request.GET.get('limite', 5))
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    datos = obtener_top_proveedores(limite, fecha_desde, fecha_hasta)
    
    return JsonResponse({
        'success': True,
        'data': datos
    })


@login_required
def api_clientes_top(request):
    """
    API endpoint para top clientes.
    """
    limite = int(request.GET.get('limite', 5))
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    datos = obtener_top_clientes(limite, fecha_desde, fecha_hasta)
    
    return JsonResponse({
        'success': True,
        'data': datos
    })


@login_required
def reporte_flujo_caja(request):
    """
    Vista dedicada al reporte de flujo de caja.
    """
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    if not fecha_desde and not fecha_hasta:
        fecha_hasta = datetime.now().date()
        fecha_desde = fecha_hasta - timedelta(days=30)
    
    datos = calcular_flujo_caja(fecha_desde, fecha_hasta)
    
    context = {
        'datos': datos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }
    
    return render(request, 'flujo_caja.html', context)


@login_required
def reporte_ventas_mensuales(request):
    """
    Vista dedicada al reporte de ventas mensuales.
    """
    anio = request.GET.get('anio', datetime.now().year)
    try:
        anio = int(anio)
    except ValueError:
        anio = datetime.now().year
    
    datos = obtener_ventas_mensuales(anio)
    
    context = {
        'datos': datos,
        'anio': anio
    }
    
    return render(request, 'ventas_mensuales.html', context)