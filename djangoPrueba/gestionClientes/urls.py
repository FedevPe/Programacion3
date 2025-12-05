from django.urls import path
from . import views

urlpatterns = [
    
    # CLIENTES
    path("clientes/", views.clientes_list, name="clientes_list"),
    path("clientes/crear/", views.cliente_crear, name="cliente_crear"),
    path("clientes/editar/<int:id>/", views.cliente_editar, name="cliente_editar"),
    path("clientes/detale/<int:id>/", views.cliente_detalle, name="cliente_detalle"),
    # path("clientes/eliminar/<int:id>/", views.cliente_eliminar, name="cliente_eliminar"),
    path("clientes/eliminar/confirmar/<int:id>/", views.cliente_confirmar_eliminar, name="cliente_confirmar_eliminar"),

]
