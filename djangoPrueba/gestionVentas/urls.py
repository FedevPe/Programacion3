from django.urls import path
from . import views

urlpatterns = [
    # Listado y CRUD de ventas
    path('', views.ventas_list, name='ventas_list'),
    path('crear/', views.ventas_form, name='ventas_crear'),
    path('editar/<int:id>/', views.ventas_form, name='ventas_editar'),
    path('detalle/<int:id>/', views.ventas_detalle, name='ventas_detalle'),
    path('eliminar/<int:id>/', views.ventas_eliminar, name='ventas_eliminar'),
    
    # Acciones de estado
    path('confirmar/<int:id>/', views.venta_confirmar, name='venta_confirmar'),
    path('cancelar/<int:id>/', views.venta_cancelar, name='venta_cancelar'),
    
    # AJAX endpoints
    path('api/producto/<int:producto_id>/', views.get_producto_info, name='get_producto_info'),
    path('api/cliente/<int:cliente_id>/', views.get_cliente_info, name='get_cliente_info'),
]