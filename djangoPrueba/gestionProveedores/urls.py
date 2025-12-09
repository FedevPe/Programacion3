from django.urls import path
from . import views

urlpatterns = [
    path('', views.proveedores_list, name='proveedores_list'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_confirmar_eliminar, name='proveedor_confirmar_eliminar'),
]