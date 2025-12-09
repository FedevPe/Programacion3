from django.urls import path
from . import views

app_name = 'gestionInformes'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_informes, name='dashboard'),
    
    # Reportes individuales (vistas completas)
    path('flujo-caja/', views.reporte_flujo_caja, name='flujo_caja'),
    path('ventas-mensuales/', views.reporte_ventas_mensuales, name='ventas_mensuales'),
    
    # API endpoints para datos dinámicos (AJAX/JSON)
    path('api/flujo-caja/', views.api_flujo_caja, name='api_flujo_caja'),
    path('api/ventas-mensuales/', views.api_ventas_mensuales, name='api_ventas_mensuales'),
    path('api/productos-top/', views.api_productos_top, name='api_productos_top'),
    path('api/proveedores-top/', views.api_proveedores_top, name='api_proveedores_top'),
    path('api/clientes-top/', views.api_clientes_top, name='api_clientes_top'),
]