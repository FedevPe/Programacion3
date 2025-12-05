from django.urls import path
from . import views

urlpatterns = [
    path('', views.compras_list, name='compras_list'),
    path('nueva/', views.compra_crear, name='compra_crear'),
    path('<int:pk>/', views.compra_detalle, name='compra_detalle'),
    path('<int:pk>/cambiar-estado/', views.compra_cambiar_estado, name='compra_cambiar_estado'),
    path('<int:pk>/eliminar/', views.compra_eliminar, name='compra_eliminar'),

   path('proveedor/<int:proveedor_id>/productos/',
     views.obtener_productos_por_proveedor,
     name='productos_por_proveedor'),
]
