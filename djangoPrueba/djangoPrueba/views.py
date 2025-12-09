from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import calendar

# modelos (ya están en tus apps, ajustar import si lo movés)
from gestionClientes.models import Cliente  # modelo Cliente. :contentReference[oaicite:4]{index=4}
from gestionProductos.models import Productos  # modelo Productos. :contentReference[oaicite:5]{index=5}
from gestionProveedores.models import Proveedor  # modelo Proveedor. :contentReference[oaicite:6]{index=6}
from gestionVentas.models import Venta  # modelo Venta. :contentReference[oaicite:7]{index=7}


@login_required
def count_active_products(request):
    """Devuelve la cantidad de productos activos."""
    count = Productos.objects.filter(activo=True).count()
    return JsonResponse({'count': count})


@login_required
def count_active_clients(request):
    """Devuelve la cantidad de clientes activos."""
    count = Cliente.objects.filter(activo=True).count()
    return JsonResponse({'count': count})


@login_required
def count_active_providers(request):
    """Devuelve la cantidad de proveedores activos."""
    count = Proveedor.objects.filter(activo=True).count()
    return JsonResponse({'count': count})


def _month_range(dt):
    """Helper: devuelve (first_day, first_day_next_month) como datetime aware."""
    # dt es timezone.now()
    year = dt.year
    month = dt.month
    first_day = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month == 12:
        next_month_first = first_day.replace(year=year+1, month=1)
    else:
        next_month_first = first_day.replace(month=month+1)
    return first_day, next_month_first


@login_required
def monthly_balance(request):
    """
    Calcula el balance del mes actual.
    Por defecto lo calculo como la suma de `total_con_iva` de las ventas CONFIRMADAS
    cuyo `fecha_venta` cae en el mes actual.
    """
    now = timezone.now()
    start, end = _month_range(now)

    agg = Venta.objects.filter(
        estado=Venta.ESTADO_CONFIRMADA,
        fecha_venta__gte=start,
        fecha_venta__lt=end
    ).aggregate(total=Sum('total_con_iva'))
    total = agg['total'] or Decimal('0.00')

    # devolver como string para evitar problemas de serialización de Decimal
    return JsonResponse({'monthly_balance': str(total)})


@login_required
def home_stats(request):
    """
    Endpoint combinado: devuelve los 4 valores en un solo JSON.
    Útil para la home si querés hacer una única llamada AJAX.
    """
    now = timezone.now()
    start, end = _month_range(now)

    products_count = Productos.objects.filter(activo=True).count()
    clients_count = Cliente.objects.filter(activo=True).count()
    providers_count = Proveedor.objects.filter(activo=True).count()

    agg = Venta.objects.filter(
        estado=Venta.ESTADO_CONFIRMADA,
        fecha_venta__gte=start,
        fecha_venta__lt=end
    ).aggregate(total=Sum('total_con_iva'))
    monthly_total = agg['total'] or Decimal('0.00')

    data = {
        'products_count': products_count,
        'clients_count': clients_count,
        'providers_count': providers_count,
        'monthly_balance': str(monthly_total)
    }
    return JsonResponse(data)