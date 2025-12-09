from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncMonth
from decimal import Decimal
from datetime import datetime, timedelta
from gestionVentas.models import Venta, DetalleVenta
from gestionCompras.models import Compra, DetalleCompra
from gestionProductos.models import Productos
from gestionProveedores.models import Proveedor
from gestionClientes.models import Cliente


def calcular_flujo_caja(fecha_desde=None, fecha_hasta=None):
    """
    Calcula ingresos (ventas) y egresos (compras) en un período.
    Retorna: {ingresos, egresos, balance}
    """
    # Filtros de fecha
    filtro_ventas = Q(estado='CONFIRMADA')
    filtro_compras = Q(estado='CONFIRMADA')
    
    if fecha_desde:
        filtro_ventas &= Q(fecha_venta__gte=fecha_desde)
        filtro_compras &= Q(fecha_compra__gte=fecha_desde)
    
    if fecha_hasta:
        filtro_ventas &= Q(fecha_venta__lte=fecha_hasta)
        filtro_compras &= Q(fecha_compra__lte=fecha_hasta)
    
    # Ingresos (ventas confirmadas)
    ingresos = Venta.objects.filter(filtro_ventas).aggregate(
        total=Sum('total_con_iva')
    )['total'] or Decimal('0.00')
    
    # Egresos (compras confirmadas)
    egresos = Compra.objects.filter(filtro_compras).aggregate(
        total=Sum('total_con_iva')
    )['total'] or Decimal('0.00')
    
    balance = ingresos - egresos
    
    return {
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': balance
    }


def obtener_ventas_mensuales(anio=None):
    """
    Obtiene las ventas agrupadas por mes para un año específico.
    Retorna: lista de diccionarios con mes y total
    """
    if not anio:
        anio = datetime.now().year
    
    ventas = Venta.objects.filter(
        estado='CONFIRMADA',
        fecha_venta__year=anio
    ).annotate(
        mes=TruncMonth('fecha_venta')
    ).values('mes').annotate(
        total=Sum('total_con_iva'),
        cantidad=Count('idVenta')
    ).order_by('mes')
    
    # Formatear para gráficos
    resultado = []
    for venta in ventas:
        resultado.append({
            'mes': venta['mes'].strftime('%B'),
            'mes_numero': venta['mes'].month,
            'total': float(venta['total']),
            'cantidad': venta['cantidad']
        })
    
    return resultado


def obtener_productos_mas_vendidos(limite=5, fecha_desde=None, fecha_hasta=None):
    """
    Obtiene los productos más vendidos por cantidad.
    """
    filtro = Q(venta__estado='CONFIRMADA')
    
    if fecha_desde:
        filtro &= Q(venta__fecha_venta__gte=fecha_desde)
    if fecha_hasta:
        filtro &= Q(venta__fecha_venta__lte=fecha_hasta)
    
    productos = DetalleVenta.objects.filter(filtro).values(
        'producto__idProducto',
        'producto__nombre',
        'producto__codProducto'
    ).annotate(
        total_vendido=Sum('cantidad'),
        ingresos_generados=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-total_vendido')[:limite]
    
    return list(productos)


def obtener_top_proveedores(limite=5, fecha_desde=None, fecha_hasta=None):
    """
    Obtiene los proveedores con más compras realizadas.
    """
    filtro = Q(compras__estado='CONFIRMADA')
    
    if fecha_desde:
        filtro &= Q(compras__fecha_compra__gte=fecha_desde)
    if fecha_hasta:
        filtro &= Q(compras__fecha_compra__lte=fecha_hasta)
    
    proveedores = Proveedor.objects.filter(filtro).annotate(
        total_compras=Count('compras'),
        monto_total=Sum('compras__total_con_iva')
    ).order_by('-total_compras')[:limite]
    
    resultado = []
    for proveedor in proveedores:
        resultado.append({
            'idProveedor': proveedor.idProveedor,
            'nombre': proveedor.razon_social,
            'total_compras': proveedor.total_compras,
            'monto_total': float(proveedor.monto_total or 0)
        })
    
    return resultado


def obtener_top_clientes(limite=5, fecha_desde=None, fecha_hasta=None):
    """
    Obtiene los clientes que más compran (por cantidad de ventas y monto).
    """
    filtro = Q(ventas__estado='CONFIRMADA')
    
    if fecha_desde:
        filtro &= Q(ventas__fecha_venta__gte=fecha_desde)
    if fecha_hasta:
        filtro &= Q(ventas__fecha_venta__lte=fecha_hasta)
    
    clientes = Cliente.objects.filter(filtro).annotate(
        total_compras=Count('ventas'),
        monto_total=Sum('ventas__total_con_iva')
    ).order_by('-monto_total')[:limite]
    
    resultado = []
    for cliente in clientes:
        resultado.append({
            'idCliente': cliente.idCliente,
            'nombre': cliente.nombre_completo(),
            'total_compras': cliente.total_compras,
            'monto_total': float(cliente.monto_total or 0)
        })
    
    return resultado


def obtener_estadisticas_generales(fecha_desde=None, fecha_hasta=None):
    """
    Obtiene estadísticas generales del negocio.
    """
    filtro_ventas = Q(estado='CONFIRMADA')
    filtro_compras = Q(estado='CONFIRMADA')
    
    if fecha_desde:
        filtro_ventas &= Q(fecha_venta__gte=fecha_desde)
        filtro_compras &= Q(fecha_compra__gte=fecha_desde)
    
    if fecha_hasta:
        filtro_ventas &= Q(fecha_venta__lte=fecha_hasta)
        filtro_compras &= Q(fecha_compra__lte=fecha_hasta)
    
    # Estadísticas de ventas
    stats_ventas = Venta.objects.filter(filtro_ventas).aggregate(
        total_ventas=Count('idVenta'),
        ingresos_totales=Sum('total_con_iva'),
        ticket_promedio=Sum('total_con_iva') / Count('idVenta')
    )
    
    # Estadísticas de compras
    stats_compras = Compra.objects.filter(filtro_compras).aggregate(
        total_compras=Count('idCompra'),
        egresos_totales=Sum('total_con_iva')
    )
    
    # Productos con bajo stock (menos de 10 unidades)
    productos_bajo_stock = Productos.objects.filter(
        stock__lt=10,
        activo=True
    ).count()
    
    return {
        'total_ventas': stats_ventas['total_ventas'] or 0,
        'ingresos_totales': stats_ventas['ingresos_totales'] or Decimal('0.00'),
        'ticket_promedio': stats_ventas['ticket_promedio'] or Decimal('0.00'),
        'total_compras': stats_compras['total_compras'] or 0,
        'egresos_totales': stats_compras['egresos_totales'] or Decimal('0.00'),
        'productos_bajo_stock': productos_bajo_stock
    }

def obtener_compras_mensuales(anio=None):
    """
    Obtiene las compras agrupadas por mes para un año específico.
    Retorna: lista de diccionarios con mes y total
    """
    if not anio:
        anio = datetime.now().year
    
    compras = Compra.objects.filter(
        estado='CONFIRMADA',
        fecha_compra__year=anio
    ).annotate(
        mes=TruncMonth('fecha_compra')
    ).values('mes').annotate(
        total=Sum('total_con_iva'),
        cantidad=Count('idCompra')
    ).order_by('mes')
    
    # Formatear para gráficos
    resultado = []
    for compra in compras:
        resultado.append({
            'mes': compra['mes'].strftime('%B'),
            'mes_numero': compra['mes'].month,
            'total': float(compra['total']),
            'cantidad': compra['cantidad']
        })
    
    return resultado